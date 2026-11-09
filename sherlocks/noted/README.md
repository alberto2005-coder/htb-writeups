---
sherlock: Noted
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, notepad++, extortion, osint, aws, windows]
---


# Noted — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Simon, desarrollador de Forela, encontró una nota de extorsión en su escritorio: alguien dice haber recogido datos sensibles de su equipo. El CERT solo entrega los **artefactos de Notepad++**, sospechando que el atacante redactó la nota y preparó el resto desde ahí. Hay una parte de **OSINT**: se pide contactar con el atacante usando servicios de terceros.

## Evidencias

```text
%APPDATA%\Notepad++\config.xml
%APPDATA%\Notepad++\backup\
%APPDATA%\Notepad++\session.xml
%APPDATA%\Notepad++\shortcuts.xml
```

## Investigación

### 1. Historial de ficheros

`config.xml` guarda la lista de recientes en objetos `File` con atributos `filename`, `path` y `encoding`. De ahí salen las rutas de los scripts que manipuló Simon y, sobre todo, los ficheros que abrió el atacante.

```bash
grep -o 'filename="[^"]*"' config.xml | sort -u
grep -o 'path="[^"]*"' config.xml | sort -u
```

Se busca un script de operaciones con AWS (nombre y ruta completa), que es la primera pregunta típica del caso y la pista de que el atacante quiso credenciales.

### 2. Copias de seguridad

En `backup\` Notepad++ deja el contenido de los documentos abiertos, incluso sin guardar:

```bash
ls -la backup/
file backup/*
strings -n 6 backup/* | head -60
```

Aquí aparece el texto de la nota de extorsión, el enlace de contacto y posiblemente contenido que Simon nunca guardó.

### 3. Sesión y pestañas

`session.xml` lista los documentos abiertos al cerrar y sus rutas; sirve para ordenar qué se abrió antes y después y para detectar ficheros que ya no existen (borrados por el atacante).

### 4. OSINT del contacto

La dirección de contacto de la nota (servicio de correo anónimo o `.onion`) se resuelve en servicios públicos. Se documenta el proveedor y el momento de creación si es visible; no se interactúa con el atacante más de lo que pida el reto.

## Conclusiones

- Acceso: el atacante trabajó **en la sesión del propio Simon** (hands-on-keyboard), no por malware automatizado.
- Objetivo: scripts y credenciales de AWS; después, la nota de extorsión.
- Prueba clave: el historial de Notepad++ pone fecha y ruta a cada acción.

## Lecciones

- Las aplicaciones de escritorio guardan mucho más de lo que el usuario cree: recientes, backups y sesión.
- El *hands-on-keyboard* se demuestra con artefactos de aplicación, no con `Prefetch` de un binario.
- Mitigación: limpiar historiales sensibles, cifrar credenciales (no guardarlas en scripts) y usar gestores de secretos.
