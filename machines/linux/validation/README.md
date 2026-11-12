---
machine: Validation
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, second-order-sqli, cookies, upload, uhc]
---

# Validation — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación de registro guarda el nombre de usuario sin sanear y lo ejecuta en una consulta posterior (SQLi de segundo orden). Con la inyección se extraen credenciales y se accede a un panel que permite subir archivos; el webshell y una mala configuración de permisos llevan a root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Se añade `validation.htb` al hosts. La web permite registrar una cuenta y muestra un panel de perfil. Se revisan cookies y parámetros.

## Acceso inicial

El campo `username` acepta una carga SQL que se almacena y se ejecuta al consultar el perfil. Se usa una carga de unión o basada en errores para volcar usuarios y contraseñas. Con las credenciales se accede al panel de administración.

Alternativa con `sqlmap` sobre la petición de login/perfil:

```bash
sqlmap -r request.txt --level 5 --risk 3 --batch
```

## Movimiento lateral

El panel permite subir un archivo. Se sube un webshell PHP y se ejecuta:

```bash
curl 'http://validation.htb/uploads/shell.php?c=id'
```

Se obtiene una shell como el usuario del servicio web.

## Escalada a root

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
```

Se identifica un binario SUID o una regla sudo mal configurada. Se abusa de ella (por ejemplo, un script que llama a un binario sin ruta absoluta) para obtener root. Se lee la flag y se redacta.

## Evidencia

- Petición de registro con la carga SQL (redactada).
- Volcado de credenciales redactado.
- Webshell y `sudo -l`/SUID.
- Shell root y flag redactada.

## Lecciones aprendidas

- La sanitización en el registro no basta si el dato se usa después.
- Las cookies y el perfil son puntos de SQLi de segundo orden.
- Un panel de subida sin validación permite RCE.
- Los permisos SUID/sudo deben revisarse tras el foothold.

## Mitigación y detección

- Consultas parametrizadas en todas las capas.
- Validar tipo y contenido de archivos subidos.
- Guardar uploads fuera del webroot y sin ejecución.
- Auditar SUID y reglas sudo.

## Referencias

- <https://www.hackthebox.com/machines/validation>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://gtfobins.github.io/>
