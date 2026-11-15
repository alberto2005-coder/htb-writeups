---
topic: Extracción de hashes de Gitea
tags: [windows, gitea, sqlite, hashcat, credentials]
---

# Extracción de hashes de Gitea

[🌐 English](gitea-sqlite-hash-extraction.en.md) | **Español**

## Concepto

Gitea guarda usuarios y hashes de contraseña en una base SQLite local. Si el servicio o un backup exponen `gitea.db`, los hashes PBKDF2 se pueden extraer y crackear fuera del host.

## Cuándo aplica

- Gitea instalado en el mismo host que la aplicación comprometida.
- Backups o volúmenes con `gitea.db` legibles.
- Contraseñas de Gitea reutilizadas por cuentas del sistema.

## Procedimiento

1. Localizar `gitea.db` y confirmar que es SQLite.
2. Volcar la tabla `user` y el campo de hash.
3. Reformatear el hash PBKDF2 al formato de Hashcat.
4. Crackear y probar la contraseña contra SSH/WinRM.

```bash
sqlite3 gitea.db '.tables'
sqlite3 gitea.db 'select name,passwd_hash from user;'
# El formato de Gitea es pbkdf2$sha256$<iteraciones>$<sal>$<hash>
hashcat -m 10900 gitea.hash /usr/share/wordlists/rockyou.txt
```

## Variantes

- Base MySQL/PostgreSQL en instalaciones mayores.
- Hash en el backup de un volumen Docker.
- Usuario administrador con hash distinto.
- Contraseña compartida con el usuario del sistema.

## Limitaciones

- La base debe ser legible por el usuario comprometido.
- PBKDF2 con muchas iteraciones ralentiza el cracking.
- El formato exacto cambia entre versiones de Gitea.

## Mitigación y detección

- Proteger `gitea.db` y los backups con permisos restrictivos.
- Usar contraseñas únicas y hashes lentos; rotar tras una intrusión.
- Monitorizar accesos a la base y autenticaciones fallidas.

## Referencias

- <https://docs.gitea.com/administration/config-cheat-sheet>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
- <https://attack.mitre.org/techniques/T1552/001/>
