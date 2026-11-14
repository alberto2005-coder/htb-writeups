---
topic: Microsoft Access y Outlook — extracción de credenciales
tags: [forensics, access, mdb, pst, credentials]
---

# Microsoft Access y Outlook — extracción de credenciales

[🌐 English](mdb-pst-credential-extraction.en.md) | **Español**

## Concepto

Los backups antiguos de Microsoft Access (`*.mdb`) y los buzones exportados de Outlook (`*.pst`) suelen conservar credenciales en tablas y correos. Son formatos habituales en shares de backup y en equipos de soporte, y permiten pasar de un archivo anónimo a una cuenta válida sin explotar ningún servicio.

## Cuándo aplica

- FTP, SMB o un backup accesible entregan archivos `.mdb`, `.pst` o ZIP antiguos.
- La aplicación usa Access como base de datos interna o guarda correos exportados.
- Se buscan credenciales reutilizadas en telnet, SSH, RDP o paneles internos.

## Procedimiento

1. Identificar los archivos con `file` y listar las tablas del MDB con `mdb-tables`.
2. Exportar las tablas de usuarios con `mdb-export` y revisar hashes o contraseñas en claro.
3. Si el ZIP está protegido, probar la contraseña recuperada de la base antes de atacarlo.
4. Convertir el PST con `readpst` y buscar correos de bienvenida, credenciales y configuraciones.

## Comandos

```bash
file backup.mdb "Access Control.zip"
mdb-tables -1 backup.mdb
mdb-export backup.mdb auth_user
readpst -o pst -S "Access Control.pst"
grep -RniE "password|passwd|credencial|usuario" pst | head
```

## Variantes

- `mdb-sql` para consultas concretas y `mdb-export` para volcar una tabla completa.
- `pffexport` o `libpff` cuando `readpst` falla con un PST dañado.
- `strings` sobre el MDB o el PST para una primera búsqueda rápida.

## Limitaciones

- Un MDB puede tener contraseña de base de datos, pero muchas herramientas la ignoran.
- La contraseña de un PST no cifra el contenido: solo controla la apertura en Outlook.
- No todos los correos son legibles si el PST está corrupto o usa un perfil cifrado.

## Mitigación

- Eliminar backups y exportaciones de correo de shares accesibles.
- Aplicar permisos mínimos y cifrado a los backups; no reutilizar contraseñas.
- Revisar la presencia de `.mdb` y `.pst` en repositorios y estaciones de soporte.

## Detección

- Accesos anómalos a archivos `.mdb`, `.pst` o ZIP de backup.
- Ejecución de `mdb-export`, `readpst` o herramientas forenses en un host de producción.
- Autenticaciones con la misma contraseña desde un origen nuevo.

## Referencias

- [0xdf — Access](https://0xdf.gitlab.io/2019/03/02/htb-access.html)
- [CWE-312 — Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
- [MDB Tools](https://www.mdbtools.ca/)
