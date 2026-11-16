---
machine: IClean
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, xss, ssti, flask, qpdf, privesc]
---

# IClean — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web de limpieza permite generar presupuestos y códigos QR. Un XSS en el campo de cita llega al bot de administración y permite robar su cookie, cuyo `role` es el MD5 de `admin`. El generador de QR es vulnerable a SSTI de Jinja y da una shell como `www-data`. La base de datos contiene el SHA-256 de `consuela`, que se crackea; esa cuenta puede ejecutar `qpdf` con sudo y adjuntar la clave privada de root a un PDF.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH y `80` Flask.
- Formulario de presupuesto, generador de QR y panel de administración.
- La web se llama Capiclean.

## Enumeración

Se revisan las rutas y el código disponible. El campo de cita se refleja sin escapar y hay un botón para que un administrador la revise. El generador de QR pasa el texto a una plantilla Jinja. En el host, `consuela` tiene un hash SHA-256 en la base de datos.

## Foothold

Se envía una cita con `<script>` o un `img onerror` para que el bot la abra y exfiltre su cookie. La cookie robada ya contiene el rol de administrador (`role` = MD5 de `admin`), así que se reutiliza para entrar en `/dashboard`. El panel permite generar QR; el parámetro llega a `render_template_string`, y `{{7*7}}` confirma la SSTI.

```text
{{ cycler.__init__.__globals__.os.popen('id').read() }}
```

## Movimiento lateral

La SSTI ejecuta comandos como `www-data`. En el código y en la base se encuentra el hash de `consuela`; `hashcat -m 1400` lo crackea y la contraseña funciona por SSH.

## Escalada de privilegios

`consuela` puede ejecutar `/usr/bin/qpdf` como root con su contraseña. `qpdf` permite crear un PDF vacío y adjuntarle cualquier archivo legible por root. Se adjunta `/root/.ssh/id_rsa`, se extrae del PDF y se usa para entrar por SSH como root.

```bash
sudo qpdf --empty --add-attachment /root/.ssh/id_rsa -- out.pdf
qpdf --show-attachment=id_rsa out.pdf
```

## Evidencia

- Cita con JavaScript y petición del bot.
- Cookie con `role` de administrador.
- `{{7*7}}` evaluado en el QR.
- PDF con la clave privada de root adjunta.

## Lecciones aprendidas

- Un XSS en una vista de administrador puede convertirse en toma de cuenta.
- Un rol derivado de un hash conocido no aporta seguridad.
- Las plantillas de Jinja nunca deben recibir texto del usuario.
- Herramientas legítimas con sudo pueden leer archivos privilegiados.

## Mitigación y detección

- Escapar la salida y usar cookies `HttpOnly`/`SameSite`.
- No derivar roles de valores adivinables; firmar y validar en el servidor.
- Usar plantillas fijas y contexto estricto en Jinja.
- Restringir `qpdf` con sudo y auditar la creación de PDFs con adjuntos.

## Referencias

- [0xdf — IClean](https://0xdf.gitlab.io/2024/08/03/htb-iclean.html)
- [IppSec — IClean](https://www.youtube.com/watch?v=DYp9TFnZH-g)
- [Hack The Box — IClean](https://app.hackthebox.com/machines/iclean)
