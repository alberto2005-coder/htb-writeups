---
topic: NSS PostgreSQL — usuarios del jail y escalada
tags: [linux, nss, postgresql, jail, privesc]
---

# NSS PostgreSQL — usuarios del jail y escalada

[🌐 English](nss-postgresql-jail.en.md) | **Español**

## Concepto

Un jail puede delegar usuarios y grupos en PostgreSQL mediante un módulo NSS. Si las credenciales de la base están en un archivo legible, el atacante puede insertar usuarios con UID 0 o con el GID de `sudo`. La autenticación del sistema confía en esas filas como si fueran `/etc/passwd` y `/etc/shadow`.

## Cuándo aplica

- `/etc/nsswitch.conf` usa un módulo como `nss-pgsql` para `passwd` o `shadow`.
- Los archivos `nss-pgsql*.conf` contienen credenciales y son legibles.
- El usuario de base tiene permisos de inserción sobre las tablas del jail.

## Procedimiento

1. Leer `nsswitch.conf` y localizar la configuración del módulo.
2. Revisar permisos de `nss-pgsql.conf` y `nss-pgsql-root.conf`.
3. Conectarse a PostgreSQL con las credenciales encontradas.
4. Insertar un usuario con UID 0 o GID privilegiado y autenticarse con `su` o SSH.

## Comandos

```bash
grep -R nss /etc/nsswitch.conf
ls -l /etc/nss-pgsql*
cat /etc/nss-pgsql-root.conf
psql -h 127.0.0.1 -U <DBUSER> -d <DB>
INSERT INTO passwd_table (username, passwd, uid, gid, homedir) VALUES ('nuevo', '<HASH>', 0, 0, '/root');
```

## Variantes

- Usar un GID de `sudo` o `wheel` en lugar de UID 0.
- Insertar una entrada en `shadow_table` para controlar la contraseña.
- Aprovechar un usuario de base con permisos de `UPDATE` sobre filas existentes.

## Limitaciones

- El módulo puede cachear usuarios y tardar en reflejar cambios.
- La base puede exigir una contraseña distinta de la del jail.
- SELinux o AppArmor pueden impedir que `su` consulte el módulo.

## Mitigación

- Restringir la lectura de `nss-pgsql*.conf` y usar credenciales de solo lectura.
- Separar la base del jail y auditar las inserciones en `passwd_table`.
- No permitir UID 0 ni GIDs privilegiados desde NSS.

## Detección

- Altas de usuarios fuera de la aplicación de gestión.
- Consultas `INSERT` a las tablas de NSS desde una sesión interactiva.
- Inicios de sesión con UID 0 para usuarios recién creados.

## Referencias

- [0xdf — RedCross](https://0xdf.gitlab.io/2019/04/13/htb-redcross.html)
- [GNU libc — Name Service Switch](https://www.gnu.org/software/libc/manual/html_node/Name-Service-Switch.html)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
