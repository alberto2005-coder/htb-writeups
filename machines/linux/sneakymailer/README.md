---
machine: SneakyMailer
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, smtp, phishing, imap, ftp, pypi, sudo]
---

# SneakyMailer — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web expone correos de empleados y el servidor SMTP permite enviar mensajes. Un usuario pulsa un enlace de phishing y entrega sus credenciales; su buzón IMAP revela acceso FTP. La subida FTP deja un webshell; un servidor PyPI interno permite ejecutar código al instalar un paquete y `sudo pip` da root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p21,22,25,80,143,993,8080 <IP>
```

- FTP, SSH, SMTP, HTTP, IMAP y un servidor PyPI.
- La web tiene una página de equipo con correos.
- El SMTP acepta conexiones y permite probar usuarios.

## Enumeración

- Se recopilan correos y se prueba un enlace de phishing con un formulario propio.
- Un usuario visita la URL y envía credenciales al servidor controlado.
- El buzón IMAP contiene credenciales de FTP.
- El FTP escribe en el directorio del vhost de desarrollo.

## Foothold

Se envía un correo con un enlace al formulario, se captura la petición y se accede al IMAP. Con las credenciales FTP se sube un PHP al vhost y se ejecuta.

```bash
swaks --to <USER> --server <IP> --body 'http://<ATTACKER>/'
curl -u <USER>:<PASS> ftp://<IP>/
```

## Escalada de privilegios

El servidor PyPI interno instala paquetes de usuarios. Se publica un paquete con un `setup.py` que ejecuta un comando; la instalación se produce como otro usuario. La regla `sudo pip` repite la ejecución como root.

```bash
python3 -m build
twine upload --repository-url http://pypi.sneakycorp.htb:8080/ dist/*
sudo -l
```

## Evidencia

- Correo enviado y credenciales capturadas.
- Acceso IMAP y credenciales FTP.
- Webshell en el vhost.
- Paquete PyPI ejecutado y root mediante `sudo pip`.

## Lecciones aprendidas

- El correo y el phishing son una superficie de acceso inicial.
- Un buzón puede contener credenciales de otros servicios.
- Los repositorios de paquetes internos ejecutan código al instalar.
- `sudo pip` equivale a ejecución como root.

## Mitigaciones y detección

- Formar usuarios y aplicar DMARC/SPF; filtrar enlaces.
- No reutilizar credenciales entre correo, FTP y aplicaciones.
- Firmar paquetes y restringir quién publica en el índice interno.
- Evitar `sudo pip`; usar entornos virtuales y permisos mínimos.
- Referencias: OWASP Phishing, PyPI security, HTB SneakyMailer.

## Referencias

- <https://www.hackthebox.com/machines/SneakyMailer>
- <https://owasp.org/www-community/attacks/Phishing>
- <https://attack.mitre.org/techniques/T1566/>
- <https://attack.mitre.org/techniques/T1546/>
