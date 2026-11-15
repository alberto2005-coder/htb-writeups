---
topic: SQLite — recuperación con WAL y SHM
tags: [windows, sqlite, wal, forensics, sticky-notes]
---

# SQLite — recuperación con WAL y SHM

[🌐 English](sqlite-wal-forensics.en.md) | **Español**

## Concepto

SQLite en modo WAL escribe las transacciones en un archivo `-wal` y usa `-shm` para el índice compartido. Si solo se copia la base principal, faltan datos recientes. Copiar los tres archivos permite abrir la base y recuperar registros que la aplicación aún no ha consolidado, como credenciales o notas.

## Cuándo aplica

- Se encuentra una base SQLite de una aplicación de escritorio.
- Existen archivos `-wal` y `-shm` junto a la base.
- La base principal parece incompleta o sin las últimas entradas.

## Procedimiento

1. Copiar la base y sus archivos `-wal`/`-shm` al mismo directorio.
2. Abrirla con `sqlite3` y listar tablas.
3. Forzar un checkpoint o consultar las tablas directamente.
4. Buscar credenciales, notas y rutas.

## Comandos

```bash
cp StickyNotes.snt StickyNotes.snt-wal StickyNotes.snt-shm /tmp/
sqlite3 /tmp/StickyNotes.snt ".tables"
sqlite3 /tmp/StickyNotes.snt "PRAGMA wal_checkpoint(FULL);"
sqlite3 /tmp/StickyNotes.snt "SELECT * FROM <TABLE>;"
```

## Variantes

- Usar `sqlite3 .recover` si la base está corrupta.
- Buscar cadenas con `strings` en el WAL.
- Aplicar la misma técnica a bases de navegadores y aplicaciones Electron.

## Limitaciones

- El WAL puede estar cifrado o vacío.
- La aplicación puede haber hecho checkpoint y borrado el WAL.
- La versión de SQLite debe ser compatible.

## Mitigación

- Cifrar bases con datos sensibles.
- Borrar WAL/SHM al cerrar y restringir su lectura.
- No guardar credenciales en texto claro.

## Detección

- Acceso a archivos `-wal`/`-shm` fuera de la aplicación.
- Copias de bases de datos de escritorio.
- Consultas a tablas de credenciales.

## Referencias

- [SQLite — WAL format](https://www.sqlite.org/wal.html)
- [0xdf — Breadcrumbs](https://0xdf.gitlab.io/2021/07/17/htb-breadcrumbs.html)
- [CWE-312 — Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
