---
challenge: Obscure
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, webshell, keepass, john, ofuscacion]
type: Forensics
---


# Obscure — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un atacante sube un **webshell PHP ofuscado** (`support.php`) con base64 + zlib + XOR y `eval`. El PCAP de los minutos previos al apagado del servicio contiene los comandos que ejecutó y de ahí sale un **`.kdbx` de KeePass**; `keepass2john` + diccionario abren la caja y aparece la flag.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Un atacante sube un **webshell PHP ofuscado** (`support.php`) con base64 + zlib + XOR y `eval`. El PCAP de los minutos previos al apagado del servicio contiene los comandos que ejecutó y de ahí sale un **`.kdbx` de KeePass**; `keepass2john` + diccionario abren la caja y aparece la flag.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- `support.php` (webshell ofuscado) y `capture.pcap`.

## Lecciones aprendidas

- **Orden de capas**: si se aplica el XOR antes del base64 no sale nada; hay que seguir el orden del código.
- **kdbx corrupto**: extraer el objeto con cuidado; una respuesta truncada invalida el fichero.
- **john lento**: el formato KeePass es costoso; probar también `hashcat -m 13400` con GPU.

- Un webshell ofuscado no oculta su comportamiento: el `eval` final delata la ejecución.
- Un PCAP de tráfico HTTP sin TLS contiene credenciales, comandos y ficheros exfiltrados.
- Un gestor de contraseñas es tan fuerte como su contraseña maestra: si está en un diccionario, cae.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [pcap-triage](../../knowledge/forensics/pcap-triage.md)
- [rop-stack](../../knowledge/pwn/rop-stack.md)

## Método

1. **Entender el webshell**: deshacer capas en orden — base64, descompresión zlib y XOR con la clave del propio código. Un `eval` al final indica que el parámetro POST ejecuta código.

```bash
grep -o "base64_decode\|gzuncompress\|gzinflate\|eval" support.php
```

2. **Leer la conversación**: en Wireshark, `http.request.method == POST` y `Follow → HTTP Stream`. Las peticiones llevan el comando en el cuerpo; las respuestas, la salida.

3. **Reconstruir la sesión**: con `ls -al` se ve un fichero interesante, `pwdb.kdbx`. Se extrae del propio flujo o con `Export Objects → HTTP`.

4. **Crackear la caja**:

```bash
keepass2john pwdb.kdbx > kdbx.hash
john --wordlist=/usr/share/wordlists/rockyou.txt kdbx.hash
```

5. **Abrir** con KeePassXC y la contraseña recuperada: dentro está la flag.
