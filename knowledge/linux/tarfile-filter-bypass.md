---
topic: Python tarfile — bypass del filtro data
tags: [linux, python, tarfile, cve-2025-4517, symlink, arbitrary-write]
---

# Python tarfile — bypass del filtro data

[🌐 English](tarfile-filter-bypass.en.md) | **Español**

## Concepto

El filtro `data` de `tarfile` intenta impedir escrituras fuera del directorio de extracción, pero CVE-2025-4517 permite saltarlo con rutas y symlinks manipulados. Si el script corre como root, se puede escribir en `/root/.ssh/authorized_keys`.

## Cuándo aplica

- Un script root extrae un tar controlado.
- Usa `tarfile.extractall(filter='data')` en una versión vulnerable.
- El destino está fuera de la vista del atacante.

## Procedimiento

1. Revisar la versión de Python y el filtro.
2. Crear un tar con symlink y ruta de escape.
3. Ejecutar la restauración como root.
4. Comprobar la clave escrita.

## Comandos

```bash
python3 -c 'import tarfile; print(tarfile.__file__)'
# construir tar con symlink a /root/.ssh/authorized_keys y ejecutar el script
```

## Variantes

- Rutas con `..` o enlaces absolutos.
- `filter='tar'` también puede ser inseguro.
- Escritura en `/etc/cron.d` o un servicio.

## Limitaciones

- Python parcheado rechaza el tar.
- El script puede validar el manifiesto.
- El destino puede ser de solo lectura.

## Mitigación

- Actualizar Python a una versión corregida.
- Validar miembros y resolver symlinks.
- Extraer como usuario sin privilegios.

## Detección

- Tars con symlinks o rutas absolutas.
- Escrituras en `/root` desde un restore.
- Ejecuciones de restauración fuera de horario.

## Referencias

- [0xdf — WingData](https://0xdf.gitlab.io/2026/06/27/htb-wingdata.html)
- [NVD — CVE-2025-4517](https://nvd.nist.gov/vuln/detail/CVE-2025-4517)
- [Python — tarfile filters](https://docs.python.org/3/library/tarfile.html#extraction-filters)
