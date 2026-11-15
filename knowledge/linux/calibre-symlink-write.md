---
topic: Calibre — escritura arbitraria por symlink
tags: [linux, calibre, symlink, file-write, privesc]
---

# Calibre — escritura arbitraria por symlink

[🌐 English](calibre-symlink-write.en.md) | **Español**

## Concepto

Un servicio que convierte ebooks con Calibre suele ejecutarse como el usuario propietario. Si acepta archivos o rutas controladas y sigue symlinks, la conversión puede escribir fuera del directorio de trabajo y modificar archivos como `.ssh/authorized_keys`.

## Cuándo aplica

- Hay un conversor Calibre interno accesible desde otro usuario.
- El servicio escribe en un directorio del usuario destino.
- Los symlinks no se resuelven ni se bloquean.

## Procedimiento

1. Localizar el puerto y el usuario del proceso (`ps`, `ss`).
2. Crear un symlink con nombre de ebook hacia el archivo destino.
3. Subirlo y lanzar la conversión.
4. Verificar la escritura e iniciar sesión con la clave.

## Comandos

```bash
ln -s /home/neil/.ssh/authorized_keys book.epub
# subir book.epub y convertir a PDF/EPUB
ssh -i id_ed25519 neil@bookworm.htb
```

## Variantes

- Symlink en el directorio de salida o en la ruta de la portada.
- Metadatos que referencian rutas absolutas.
- Conversión en lote con nombres controlados.

## Limitaciones

- El servicio puede usar un usuario sin home o sin `.ssh`.
- Un `realpath` o `O_NOFOLLOW` bloquea el ataque.
- Los contenedores de solo lectura impiden la escritura.

## Mitigación

- Resolver rutas y rechazar symlinks.
- Ejecutar el conversor con un usuario sin acceso a `.ssh`.
- Montar el directorio de trabajo con `noexec,nosuid` y permisos mínimos.

## Detección

- Symlinks inesperados en uploads o directorios de salida.
- Escrituras en `.ssh` desde un proceso de conversión.
- Picos de CPU de `ebook-convert` fuera de horario.

## Referencias

- [0xdf — Bookworm](https://0xdf.gitlab.io/2024/01/20/htb-bookworm.html)
- [Calibre — ebook-convert](https://manual.calibre-ebook.com/generated/en/ebook-convert.html)
- [CWE-59 — Link Following](https://cwe.mitre.org/data/definitions/59.html)
