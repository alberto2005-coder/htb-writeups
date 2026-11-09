# Sherlocks — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

Los **Sherlocks** son escenarios de investigación defensiva: no se ataca nada, se responde a preguntas sobre un incidente a partir de evidencias (imágenes de memoria, volcados de disco, logs, PCAP, binarios). Este directorio recoge las fichas de los que voy documentando, con el escenario, las herramientas y el razonamiento; no se publican respuestas literales de la plataforma.

## Cómo funciona

1. Se descarga un ZIP con las evidencias (contraseña habitual: `hacktheblue`).
2. Dentro hay un `README` con el escenario y las preguntas.
3. Se responde en la plataforma; cada respuesta correcta da puntos.

Los artefactos pueden contener malware real: se trabaja en una VM aislada y sin red.

## Fichas

| Sherlock | Dominio | Dificultad | Evidencia principal | Herramientas | Ficha |
|---|---|---|---|---|---|
| Litter | SOC | Easy | PCAP + ZIP de un host de pruebas | Wireshark, dnscat2-decoder | [Ver](litter/README.md) |
| PhantomRing | Malware Analysis | Very Easy | Binario ELF de post-explotación | Ghidra, `strings`, `file` | [Ver](phantomring/README.md) |
| Opportunist | DFIR / Malware | Medium | Memoria + triaje de un equipo corporativo | Volatility 3, VirusTotal, ChromeCacheView, SQLECmd | [Ver](opportunist/README.md) |
| dOOMs Day | DFIR | Medium | Logs web de un servidor PHP comprometido | análisis de access logs, PHP2Shell | [Ver](dooms-day/README.md) |
| Brutus | DFIR | Very Easy | Logs de autenticación | `grep`, `awk`, timeline | [Ver](brutus/README.md) |
| MangoBleed | DFIR | Very Easy | Triaje de Windows | EvtxECmd, timeline | [Ver](mangobleed/README.md) |
| NeuroSync-D | DFIR | Easy | Artefactos de un fabricante de dispositivos médicos | RegRipper, MFT | [Ver](neurosync-d/README.md) |
| Campfire-1 | DFIR / Active Directory | Easy | Logs de eventos de un dominio | EvtxECmd, análisis de 4769 | [Ver](campfire-1/README.md) |
| CrownJewel-1 | DFIR / Active Directory | Medium | Telemetría de DC tras un compromiso | Eventos 4662/4769, correlación | [Ver](crownjewel-1/README.md) |
| Loggy | DFIR | Very Easy | Logs de un servidor web | `awk`, `grep`, línea de tiempo | [Ver](loggy/README.md) |
| Bumblebee | Malware Analysis | Medium | Cargador en contenedor ISO con LNK | `strings`, análisis de LNK, `Amcache` | [Ver](bumblebee/README.md) |

## Metodología común

1. **Inventario**: listar ficheros, tamaños y hashes antes de abrir nada. Anotar qué es original y qué se ha generado.
2. **Contexto**: leer el escenario dos veces y escribir qué se busca (quién, cuándo, cómo, qué se llevó).
3. **Triaje**: empezar por lo que da línea temporal rápida (ejecución, logins, conexiones) y no por el detalle.
4. **Correlación**: cruzar dos fuentes para cada conclusión; una sola no vale como evidencia.
5. **Respuesta**: redactar en formato "pregunta → evidencia → razonamiento", con rutas y hashes.

## Convenciones

- Una carpeta por Sherlock con `README.md` y `README.en.md`.
- Nunca se copian respuestas de la plataforma; se documenta el método y la evidencia.
- Plantilla: `templates/sherlock-template.md` y `.en.md`.
- El Sherlock **Rameh** todavía no está identificado en el catálogo de HTB; queda como pendiente de confirmar nombre y dominio antes de escribir su ficha.
