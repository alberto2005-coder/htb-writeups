---
machine: Precious
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ruby, pdfkit, ssrf, yaml-deserialization, sudo]
---

# Precious — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación convierte una URL en PDF con `pdfkit` y permite apuntar a recursos internos. La lectura de archivos y la versión vulnerable de `pdfkit` llevan a ejecución de comandos como el usuario del servicio. Un script Ruby ejecutado con `sudo` y un YAML controlable permiten escalar a root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH y HTTP.
- El sitio se anuncia como conversor de páginas web a PDF.
- `robots.txt` y los errores revelan la tecnología Ruby.

## Enumeración

- El formulario recibe una URL y devuelve un PDF.
- `pdfkit` acepta esquemas como `file://` y rutas internas.
- La respuesta incluye metadatos del generador y la versión.
- Hay una aplicación interna y un script de mantenimiento ejecutado por root.

## Foothold

Se prueba primero una lectura inocua de `/etc/passwd` mediante `file://`. Después se usa la inyección de opciones de `pdfkit`/`wkhtmltopdf` para ejecutar un comando y obtener una reverse shell como el usuario del servicio.

```bash
curl -s 'http://precious.htb/' --data-urlencode 'url=file:///etc/passwd'
```

La versión vulnerable permite inyectar parámetros en la línea de comandos; se usa un callback controlado para confirmar la ejecución antes de estabilizar la shell.

## Escalada de privilegios

El usuario puede ejecutar con `sudo` un script Ruby de actualización. El script carga un YAML de una ruta escribible; se sustituye por un objeto Ruby que ejecuta un comando al deserializarse.

```bash
sudo -l
find / -writable -type f 2>/dev/null | head
```

Se valida el cambio en local, se ejecuta el script con `sudo` y se comprueba el resultado sin publicar la flag.

## Evidencia

- PDF generado a partir de una URL interna.
- Lectura de un archivo del sistema.
- `id` como usuario del servicio.
- Ejecución de `sudo` sobre el script Ruby y root.

## Lecciones aprendidas

- Un conversor de URLs es una superficie SSRF y de lectura de archivos.
- Los metadatos del PDF identifican la versión exacta de la librería.
- La deserialización YAML en Ruby puede ejecutar objetos.
- Un script de mantenimiento con `sudo` merece una revisión completa.

## Mitigaciones y detección

- Restringir esquemas, hosts y puertos permitidos en el conversor.
- Actualizar `pdfkit` y `wkhtmltopdf`; no concatenar opciones.
- Usar `YAML.safe_load` y permisos mínimos en scripts con `sudo`.
- Alertar de peticiones a `127.0.0.1`, `file://` y cambios en scripts de mantenimiento.
- Referencias: CVE-2022-25765, OWASP SSRF, HTB Precious.

## Referencias

- <https://www.hackthebox.com/machines/Precious>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-25765>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1190/>
