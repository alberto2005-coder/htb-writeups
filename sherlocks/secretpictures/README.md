---
sherlock: SecretPictures
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, golang, worm, usb, registry, c2, base64]
---

# SecretPictures — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin muestra original ni IOC reales.

## TL;DR

Un gusano escrito en Go se copia a unidades USB, crea un directorio oculto y persiste mediante `Run`. Se comunica con un C2 y ejecuta comandos en Base64. El análisis estático y de artefactos reconstruye la propagación.

## Escenario

Varios equipos muestran una carpeta oculta y conexiones salientes. Se entrega una muestra y artefactos de un host para identificar el gusano y su alcance.

## Artefactos

- Binario Go y cadenas.
- `Run`/`RunOnce`, tareas y servicios.
- `$MFT`, `$Usb` y logs de USBSTOR.
- PCAP y archivos en `%APPDATA%`.

## Metodología

1. Se identifica Go por secciones, imports y cadenas.
2. Se localizan rutas de USB, nombres de carpeta y claves `Run`.
3. Se revisan eventos de conexión USB y creación de archivos.
4. Se decodifican comandos Base64 y se extrae el C2.
5. Se mapean hosts afectados por el mismo hash.

```bash
strings -n 8 sample.exe | grep -iE 'http|usb|run|base64'
```

## Preguntas tipo

- ¿En qué lenguaje está escrito?
- ¿Qué rutas USB utiliza para propagarse?
- ¿Qué clave de registro usa para persistir?
- ¿Cuál es el C2 y el formato de comandos?
- ¿Qué hosts muestran el mismo IOC?

## Herramientas

`Detect It Easy`, `Ghidra`, `strings`, `Registry Explorer`, `Wireshark`.

## Evidencia y redacción

Se conservan hashes, rutas y capturas con IPs, usuarios y nombres de archivo redactados.

## Lecciones aprendidas

- Go deja cadenas e imports reconocibles.
- Los gusanos USB combinan propagación y persistencia.
- Base64 no es cifrado.
- El alcance se mide por hash y artefactos, no por nombres.

## Detección

- Bloquear ejecución desde USB.
- Monitorizar `Run` y carpetas ocultas.
- Alertar de conexiones periódicas.
- Aplicar YARA por familia y hash.

## Referencias

- <https://app.hackthebox.com/sherlocks/SecretPictures>
- <https://attack.mitre.org/techniques/T1091/>
- <https://attack.mitre.org/techniques/T1547/001/>
