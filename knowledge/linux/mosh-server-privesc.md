---
title: mosh-server — una sesión root en localhost
tags: [linux, mosh, privesc, sudo, gtfobins]
---

# mosh-server — una sesión root en localhost

[🇬🇧 English](mosh-server-privesc.en.md) | **Español**

## Concepto

`mosh-server` crea un servidor UDP y devuelve una clave efímera (`MOSH_KEY`). Si `sudo` permite ejecutarlo como root, el cliente puede conectarse a `127.0.0.1` con esa clave y obtener una shell con los privilegios del servidor.

## Cuándo aplica

- `sudo -l` incluye `mosh-server` sin restricciones.
- El binario está instalado y el puerto UDP local está libre.
- El usuario puede ejecutar `mosh-client`.

## Procedimiento

1. Comprobar la regla de sudo.
2. Lanzar `mosh-server` como root; anotar puerto y clave.
3. Exportar `MOSH_KEY` y conectar con `mosh-client` a localhost.
4. Confirmar `id` y leer la flag.

```bash
sudo -l
sudo mosh-server new -c 256 -s
# MOSH CONNECT 60001 <KEY>
MOSH_KEY=<KEY> mosh-client 127.0.0.1 60001
```

## Variantes

- Usar `script -qc` o `socat` si `mosh-client` no está.
- El puerto puede elegirse con `-p`; comprobar que no esté ocupado.
- Si `sudo` pide contraseña, reutilizar credenciales obtenidas antes.

## Limitaciones

- `mosh-server` debe estar permitido por sudo.
- La clave caduca si el servidor se detiene.
- El cliente necesita UDP local y un terminal interactivo.

## Mitigación y detección

- No permitir `mosh-server` como root en sudoers.
- Restringir binarios por ruta y argumentos.
- Auditar sesiones `mosh` y procesos hijos de sudo.
- Usar `NOEXEC` o un wrapper para comandos interactivos.

## Referencias

- <https://mosh.org/>
- <https://man7.org/linux/man-pages/man1/mosh-server.1.html>
- <https://gtfobins.github.io/gtfobins/mosh-server/>
