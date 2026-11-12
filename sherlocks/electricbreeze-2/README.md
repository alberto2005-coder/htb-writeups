---
sherlock: ElectricBreeze-2
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, java, jar, webshell, credential-theft, volt-typhoon]
---

# ElectricBreeze-2 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin muestra original ni IOC reales.

## TL;DR

Muestra JAR asociada a un actor tipo Volt Typhoon. Se descompila el bytecode, se identifica el webshell, la ofuscación, la comunicación cifrada y el acceso a credenciales.

## Escenario

Un servidor Java muestra un archivo JAR no inventariado y conexiones salientes. Se entrega la muestra y logs para determinar su función y persistencia.

## Artefactos

- JAR y clases compiladas.
- Configuración/recursos embebidos.
- Logs de proceso y red.
- Webroot y archivos creados.

## Metodología

1. Se calcula el hash y se lista el contenido del JAR.
2. Se descompila con `jadx`/`CFR` y se revisan clases de arranque.
3. Se localizan cadenas de webshell, comandos y URLs.
4. Se identifica el cifrado/configuración del C2.
5. Se correlaciona con el proceso Java y el webroot.

```bash
unzip -l sample.jar
jadx sample.jar -d out
grep -R "Runtime.getRuntime" out
```

## Preguntas tipo

- ¿Qué clase implementa el webshell?
- ¿Qué parámetros acepta y qué ejecuta?
- ¿Cómo cifra la comunicación?
- ¿Qué credenciales o archivos lee?
- ¿Cómo se inicia y persiste?

## Herramientas

`jadx`, `CFR`, `unzip`, `strings`, `Wireshark`.

## Evidencia y redacción

Se conservan hashes, clases y capturas con URLs, usuarios y rutas redactados.

## Lecciones aprendidas

- Java es fácil de descompilar y leer.
- Los webshells JSP/Java suelen usar `Runtime.exec`.
- La configuración embebida revela C2 y claves.
- Un JAR mal ubicado puede ejecutarse al desplegar.

## Detección

- Inventariar JARs y hashes en servidores.
- Alertar de `Runtime.exec` desde aplicaciones web.
- Revisar conexiones salientes de Java.
- Aplicar YARA a archivos JAR/clases.

## Referencias

- <https://app.hackthebox.com/sherlocks/ElectricBreeze-2>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://github.com/skylot/jadx>
