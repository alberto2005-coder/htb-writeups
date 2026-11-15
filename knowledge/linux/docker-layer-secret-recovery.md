---
topic: Docker — secretos en capas de imagen
tags: [linux, docker, layers, secrets, forensics]
---

# Docker — secretos en capas de imagen

[🌐 English](docker-layer-secret-recovery.en.md) | **Español**

## Concepto

Una imagen Docker es una pila de capas inmutables. Borrar un archivo en una capa posterior no lo elimina de las anteriores, y `docker save` conserva todo el historial. Un backup o un registro accesible permite extraer `.env`, claves y código fuente que se creían borrados.

## Cuándo aplica

- Hay acceso a un backup, a un registro o a una imagen de la aplicación.
- El código se distribuye en capas y se eliminan secretos en pasos posteriores.
- Se busca configuración, credenciales o código fuente.

## Procedimiento

1. Obtener la imagen o el backup y ejecutar `docker save`.
2. Extraer el tar y revisar `manifest.json` y las capas.
3. Buscar `.env`, claves, historial y archivos eliminados.
4. Reutilizar los secretos en la aplicación o en SSH.

## Comandos

```bash
docker save <IMAGE> -o image.tar
mkdir image && tar -xf image.tar -C image
find image -name ".env" -o -name "*.pem" -o -name "*.key"
docker history --no-trunc <IMAGE>
```

## Variantes

- Inspeccionar capas con `dive`.
- Buscar en `layer.tar` archivos con `tar -tvf`.
- Recuperar variables de entorno de `config.json`.

## Limitaciones

- La imagen puede usar multi-stage y no incluir las capas de build.
- Los secretos pueden estar en un volumen, no en la imagen.
- El registro puede exigir autenticación.

## Mitigación

- Usar multi-stage builds y `.dockerignore`.
- No copiar secretos en la imagen; usar secretos de runtime.
- Escanear imágenes y limitar el acceso al registro.

## Detección

- Imágenes con `.env` o claves en capas.
- Acceso anómalo al registro o a backups.
- Variables de entorno sensibles en `config.json`.

## Referencias

- [0xdf — Bolt](https://0xdf.gitlab.io/2022/02/19/htb-bolt.html)
- [Docker — Image layers](https://docs.docker.com/storage/storagedriver/)
- [CWE-312 — Cleartext Storage of Sensitive Information](https://cwe.mitre.org/data/definitions/312.html)
