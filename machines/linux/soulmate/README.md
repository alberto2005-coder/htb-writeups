---
machine: Soulmate
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, crushftp, erlang, ssh, cve-2025-32433]
---

# Soulmate — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

CrushFTP permite un bypass de autenticación (CVE-2025-31161) y acceso administrativo para subir una webshell. La escalada abusa de Erlang/OTP SSH CVE-2025-32433 y de una consola Erlang que corre como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80,443,8080 <IP>
curl -k https://soulmate.htb:8080/ | grep -i crushftp
# CVE-2025-31161
python3 crushftp_bypass.py -u https://soulmate.htb:8080
# CVE-2025-32433
python3 erlang_ssh_rce.py -t <IP> -p 2222 -c "id"
```

## Enumeración

- CrushFTP expuesto con una versión vulnerable.
- Acceso administrativo tras el bypass y capacidad de subir archivos.
- Servicio Erlang/OTP SSH en un puerto no estándar.

## Acceso inicial

El bypass de autenticación de CrushFTP permite entrar como administrador. Se sube un archivo JSP o un script interpretado y se obtiene una shell como el usuario del servicio.

## Escalada de privilegios

El servicio Erlang/OTP SSH es vulnerable a CVE-2025-32433: se envía un mensaje de autenticación antes de completar el handshake y se ejecuta código en la consola Erlang, que corre como root.

## Evidencia

- Bypass de CrushFTP y webshell.
- Acceso a la consola Erlang.
- `id` como root desde la consola.

## Lecciones aprendidas

- Los appliances de transferencia de archivos concentran privilegios.
- Un bypass de autenticación suele ser suficiente para subir código.
- Erlang/OTP SSH mal parcheado puede ejecutar comandos antes de autenticar.

## Mitigación y detección

- Actualizar CrushFTP y Erlang/OTP.
- Restringir la administración a loopback y exigir MFA.
- Monitorizar subidas y conexiones SSH anómalas.

## Referencias

- [0xdf — Soulmate](https://0xdf.gitlab.io/2026/02/14/htb-soulmate.html)
- [NVD — CVE-2025-32433](https://nvd.nist.gov/vuln/detail/CVE-2025-32433)
- [Hack The Box — Soulmate](https://app.hackthebox.com/machines/soulmate)
