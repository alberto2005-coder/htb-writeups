---
machine: Europa
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, preg_replace, cron, php]
---

# Europa — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El login es vulnerable a SQLi y permite entrar como administrador. Una llamada antigua a `preg_replace` con `/e` ejecuta código PHP y da una shell; un cron de root ejecuta un script que no existe pero es escribible por `www-data`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
gobuster dir -u https://europa.htb -w /usr/share/wordlists/dirb/common.txt -k
# Bypass de login
curl -k -d "username=admin' OR 1=1-- -&password=x" https://europa.htb/login.php
# Ejecución con preg_replace /e
curl -k "https://europa.htb/admin/search.php?q=system('id')"
pspy64 -pf -i 1000
```

## Enumeración

- Portal HTTPS con login y panel de administración.
- Parámetros que llegan a una función PHP antigua con `preg_replace` y `/e`.
- Un cron de root referencia un script ausente en una ruta escribible.

## Acceso inicial

Con `' OR 1=1-- -` se evita la autenticación. En el panel, el parámetro vulnerable pasa por `preg_replace` con el modificador `/e`, que evalúa la sustitución; se envía una reverse shell y se obtiene `www-data`.

## Escalada de privilegios

`pspy` muestra un cron de root que ejecuta un script inexistente en una ruta controlable. Se crea el archivo con una shell y, en la siguiente ejecución, el comando corre como root.

## Evidencia

- Bypass de login con SQLi.
- Ejecución de `id` mediante `preg_replace /e`.
- Script creado en la ruta del cron y shell de root.

## Lecciones aprendidas

- Los modificadores obsoletos de PHP convierten una sustitución en ejecución.
- Un cron que llama a un archivo ausente es una puerta si el directorio es escribible.
- La SQLi de autenticación sigue siendo una entrada viable.

## Mitigación y detección

- Migrar a `preg_replace_callback` y actualizar PHP.
- Usar rutas absolutas y directorios no escribibles en cron.
- Parametrizar las consultas y aplicar MFA al panel.

## Referencias

- [0xdf — Europa](https://0xdf.gitlab.io/2021/02/02/htb-europa.html)
- [PHP — preg_replace](https://www.php.net/manual/en/function.preg-replace.php)
- [Hack The Box — Europa](https://app.hackthebox.com/machines/europa)
