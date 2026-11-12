---
machine: Jarvis
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, phpmyadmin, cve-2018-12613, systemctl, suid]
---

# Jarvis — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El sitio de reservas es inyectable y permite volcar credenciales de phpMyAdmin. La versión vulnerable de phpMyAdmin permite LFI/RCE y una shell. Un binario `systemctl` con SUID completa la escalada a root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,64999 <IP>
```

Se añade `supersecurehotel.htb` al hosts. El panel de administración corre en el puerto 64999 y expone phpMyAdmin.

## Acceso inicial

El parámetro de habitación es inyectable. Con `sqlmap` o una carga manual se extraen usuarios y hashes:

```bash
sqlmap -r room.txt --batch --dbs
```

Las credenciales permiten entrar en phpMyAdmin. La versión es vulnerable a CVE-2018-12613 (LFI en `index.php`), que permite incluir archivos locales o ejecutar código si se controla una ruta.

## Movimiento lateral

Con el LFI se lee configuración y se localiza una credencial reutilizada. También se puede escribir un PHP en una ruta incluida y ejecutar comandos:

```bash
curl 'http://<IP>:64999/index.php?target=db_sql.php%253f/../../../../etc/passwd'
```

Se obtiene una shell como `www-data`.

## Escalada a root

```bash
find / -perm -4000 -type f 2>/dev/null
```

Se localiza un `systemctl` SUID. Se abusa de él para lanzar un servicio o ejecutar un comando como root:

```bash
systemctl --version
```

Con `systemctl` SUID se puede iniciar una unidad controlada o invocar `ExecStart` con un binario propio; el proceso resultante es root.

## Evidencia

- Petición SQLi y volcado redactado.
- Acceso a phpMyAdmin y versión.
- LFI y shell.
- `systemctl` SUID y shell root.

## Lecciones aprendidas

- Una SQLi en un panel secundario puede dar acceso a la base.
- phpMyAdmin antiguo es un objetivo de LFI/RCE.
- Los SUID de `systemctl` son escalada directa.
- Conviene revisar puertos altos, no solo 80/443.

## Mitigación y detección

- Parametrizar consultas y limitar errores.
- Actualizar phpMyAdmin y restringir su exposición.
- Eliminar SUID innecesarios.
- Monitorizar creación de unidades y procesos root.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2018-12613>
- <https://www.hackthebox.com/machines/jarvis>
- <https://gtfobins.github.io/gtfobins/systemctl/>
