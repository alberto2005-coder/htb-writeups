---
machine: AI
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, audio, jdwp, tomcat, privesc]
---

# AI — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web transcribe audio y pasa el texto reconocido a una consulta SQL sin parametrizar. La inyección permite leer credenciales y entrar por SSH como `alexa`. Tomcat corre como root con el depurador JDWP escuchando en `localhost:8000`; un túnel SSH y `jdwp-shellifier` ejecutan comandos como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH y `80` Apache.
- Tomcat (8080), MySQL 5.7 (3306) y JDWP (8000) escuchan solo en localhost.
- La web pide un `.wav` y devuelve la transcripción y el resultado de una búsqueda.

## Enumeración

`gobuster` encuentra `ai.php`, `intelligence.php`, `db.php` y `/uploads`. `intelligence.php` explica el modelo de voz aceptado (voz masculina de EE. UU.) y `ai.php` es el formulario de subida. `db.php` no devuelve nada por sí solo, lo que sugiere que se incluye desde otra página.

## Foothold

Se genera el audio con `flite` y se envía por `curl`. Una frase como «open single quote» demuestra que el texto se concatena en SQL. Variantes con `union select` permiten extraer versión, tablas y credenciales. Las credenciales de `alexa` funcionan por SSH.

```bash
flite -w /tmp/q.wav -voice rms -t "open single quote"
curl -s -X POST http://<IP>/ai.php \
  -F 'fileToUpload=@/tmp/q.wav;type=audio/x-wav' \
  -F 'submit=Process It!'
```

## Movimiento lateral

No hace falta pivote: `alexa` ya está en el host. `ps auxww` muestra que Tomcat se lanza como root con `-agentlib:jdwp=transport=dt_socket,server=y,address=localhost:8000`.

## Escalada de privilegios

JDWP no autentica a quien se conecta. Se reenvía el puerto local con SSH y se usa `jdwp-shellifier` para crear un objeto `Runtime` y ejecutar un script.

```bash
ssh -L 223:localhost:8000 alexa@<IP>
python3 jdwp-shellifier.py -t 127.0.0.1 -p 223 --cmd '/dev/shm/x.sh'
```

## Evidencia

- Transcripción con error SQL al introducir una comilla.
- `ps` con Tomcat como root y `address=localhost:8000`.
- Conexión de `jdwp-shellifier` y shell de root.

## Lecciones aprendidas

- La voz también es entrada de usuario: el texto transcrito llega a SQL.
- Un puerto ligado a `localhost` no es seguro si hay SSH.
- JDWP es ejecución remota sin autenticación por diseño.
- Automatizar la generación de audio ahorra tiempo en la explotación.

## Mitigación y detección

- Consultas parametrizadas y validación del texto reconocido.
- Nunca habilitar JDWP en producción; si se necesita, exigir túnel y autenticación de red.
- Ejecutar Tomcat con un usuario sin privilegios y sin capabilities.
- Detectar `-agentlib:jdwp` en líneas de proceso y conexiones a `8000`.

## Referencias

- [0xdf — AI](https://0xdf.gitlab.io/2020/01/25/htb-ai.html)
- [IppSec — AI](https://www.youtube.com/watch?v=7n7YRntu3bc)
- [Hack The Box — AI](https://app.hackthebox.com/machines/ai)
