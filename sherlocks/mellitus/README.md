---
sherlock: Mellitus
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, memory, volatility, chrome-history, hashdump, stego]
---

# Mellitus — Hack The Box Sherlock

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Pendiente de confirmar en HTB sin sesión; ficha de referencia no jugada.
> Sin flags, hashes ni credenciales reales.

## TL;DR

El ZIP entrega `memory_dump.vmem` y el snapshot de VMware `memory_dump.vmsn`. Volatility 3 reconstruye procesos, conexiones, historial de Chrome y hashes locales. La cadena pasa por un navegador que descarga una imagen; la imagen está invertida y oculta la flag. El historial de Chrome y los ficheros recuperados dan el contexto que la memoria sola no explica.

## Preparación

```bash
unzip mellitus.zip
file memory_dump.vmem memory_dump.vmsn
vol -f memory_dump.vmem windows.info
```

El `.vmsn` es el estado del snapshot: sirve para validar la coherencia del `.vmem`, no se analiza como un volcado independiente.

## 1. Procesos y línea de comandos

```bash
vol -f memory_dump.vmem windows.pslist
vol -f memory_dump.vmem windows.pstree
vol -f memory_dump.vmem windows.cmdline
```

Se buscan procesos de navegador, descargas recientes y ejecutables en `Downloads`/`Temp`. La hora del volcado se usa como referencia; todas las marcas se normalizan a UTC.

## 2. Red

```bash
vol -f memory_dump.vmem windows.netscan
```

Interesan las conexiones del navegador y cualquier proceso de usuario con salida a Internet. Se anotan como `<REMOTE_IP>:<PORT>`; no se publican IPs reales.

## 3. Historial de Chrome

El historial está en `Users/<USER>/AppData/Local/Google/Chrome/User Data/Default/History` (SQLite). Se localiza con `filescan` y se vuelca:

```bash
vol -f memory_dump.vmem windows.filescan | grep -i 'History'
vol -f memory_dump.vmem windows.dumpfiles --virtaddr <OFFSET>
sqlite3 History "select url,title,last_visit_time from urls order by last_visit_time desc limit 30;"
sqlite3 History "select target_path,tab_url from downloads;"
```

- `urls` da la página visitada y el título.
- `downloads` da el fichero descargado y la URL de origen.
- `visits` permite reconstruir la secuencia, no solo la última visita.

## 4. Hashes y credenciales

```bash
vol -f memory_dump.vmem windows.hashdump
vol -f memory_dump.vmem windows.lsadump
```

Se obtienen hashes locales para el informe, pero no se publican ni se crackean en la ficha. La presencia de una cuenta nueva o de un hash de administrador fuera de contexto es el hallazgo.

## 5. La imagen invertida

La imagen descargada se ve extraña: los colores están invertidos. Se corrige con ImageMagick o Pillow:

```bash
convert suspicious.png -negate fixed.png
python3 - <<'PY'
from PIL import Image, ImageOps
ImageOps.invert(Image.open('suspicious.png').convert('RGB')).save('fixed.png')
PY
```

Tras invertir, aparece texto o un código. Se revisan también metadatos y planos de bits por si la flag no está solo en la imagen visible:

```bash
exiftool suspicious.png
zsteg -a suspicious.png
```

## 6. Correlación

| Evidencia | Pregunta que responde |
|---|---|
| `pslist`/`cmdline` | qué se ejecutó y con qué argumentos |
| `netscan` | a dónde se conectó |
| `History` | qué descargó el usuario y desde qué página |
| `hashdump` | qué credenciales había en memoria |
| imagen invertida | cuál es el dato final |

## Lecciones aprendidas

- El snapshot `.vmsn` no sustituye al `.vmem`, pero ayuda a fechar el estado.
- El historial de Chrome está en SQLite y sobrevive en memoria; es una mina para descargas.
- Una imagen “rara” puede ser solo una inversión de color; probar `-negate` antes que estego compleja.
- Los hashes locales se documentan con cuidado: no son la flag y no deben publicarse.
- La correlación navegador → descarga → fichero es la línea principal.

## Mitigaciones y detección

- Retención de historial de navegador y telemetría de descargas en el endpoint.
- Alertar de descargas de imágenes desde dominios no categorizados y de ejecución posterior.
- Volcar memoria antes de apagar un equipo comprometido.
- Detección: procesos de navegador con conexiones anómalas, descargas a `Temp` y cuentas locales nuevas.

MITRE: T1204.002, T1105, T1555.003, T1003. SAM.

## Referencias

- <https://itsrad.io/blog/2025/Mellitus-Write-Up>
- <https://mwalkowski.com/post/sherlock-mellitus>
- <https://github.com/volatilityfoundation/volatility3>
