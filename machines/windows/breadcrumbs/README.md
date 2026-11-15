---
machine: Breadcrumbs
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, php, jwt, sqlite, sqli, aes]
---

# Breadcrumbs — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un traversal en PHP permite leer el código y forjar la cookie de sesión/JWT para entrar como administrador. Sticky Notes y una SQLite con WAL/SHM llevan a otro usuario; una SQLi UNION y la clave AES permiten llegar a administrador.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,445,3389,5985 <IP>
gobuster dir -u http://breadcrumbs.htb -w /usr/share/wordlists/dirb/common.txt
# Traversal y forja de cookie
curl -s "http://breadcrumbs.htb/download.php?file=../../../../var/www/html/index.php"
# SQLite con WAL/SHM
cp StickyNotes.snt StickyNotes.snt-wal StickyNotes.snt-shm /tmp/
sqlite3 /tmp/StickyNotes.snt ".tables"
# SQLi UNION
sqlmap --url "http://breadcrumbs.htb/portal.php" --data="search=test" --batch --dump
```

## Enumeración

- Aplicación PHP con parámetros de archivo y cookies de sesión.
- Sticky Notes y una base SQLite con archivos `-wal` y `-shm`.
- Gestor de contraseñas con una consulta SQLi.

## Acceso inicial

El traversal lee el código fuente y revela cómo se firma la sesión. Se forja una cookie con rol de administrador, se sube una webshell y se obtiene ejecución en IIS.

## Escalada de privilegios

Sticky Notes guarda credenciales de otro usuario. La SQLite se copia con sus archivos WAL/SHM para recuperar datos no consolidados; una SQLi UNION en el gestor extrae el material cifrado y la clave AES, que permite descifrar y acceder como administrador.

## Evidencia

- Código PHP leído por traversal.
- Cookie de administrador forjada y webshell.
- SQLite con WAL/SHM y secreto AES descifrado.

## Lecciones aprendidas

- Los archivos WAL/SHM contienen datos que no aparecen en la base principal.
- Una cookie firmada con un secreto filtrado es una puerta directa.
- La SQLi puede exponer claves que protegen otros secretos.

## Mitigación y detección

- No incluir secretos de firma en el código accesible.
- Cifrar y proteger las bases de Sticky Notes y del gestor.
- Parametrizar consultas y borrar archivos temporales de SQLite.

## Referencias

- [0xdf — Breadcrumbs](https://0xdf.gitlab.io/2021/07/17/htb-breadcrumbs.html)
- [SQLite — WAL format](https://www.sqlite.org/wal.html)
- [Hack The Box — Breadcrumbs](https://app.hackthebox.com/machines/breadcrumbs)
