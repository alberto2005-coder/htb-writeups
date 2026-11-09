---
sherlock: Bumblebee
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware-analysis, loader, iso, lnk, dll-sideloading]
---

# Bumblebee — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; sin respuestas literales de la plataforma.

## Escenario

Un equipo ejecuta un cargador desconocido llegado por correo. Se entrega la muestra y artefactos del host; hay que documentar el mecanismo de carga, las técnicas de evasión y los indicadores para bloquearlo.

## Evidencias

- Contenedor de la muestra (ISO/IMG o ZIP con LNK).
- Binarios acompañantes (DLL legítima + DLL maliciosa).
- Artefactos del host: `Prefetch`, `Amcache`, historial de ejecución.

## Investigación

### 1. Anatomía del contenedor

Los cargadores tipo **BumbleBee** llegan en un contenedor que Windows monta como unidad y que contiene un acceso directo y una carpeta con la carga útil. Al abrir el LNK se ejecuta un binario legítimo (`rundll32`, `wscript`, un ejecutable firmado) que carga la DLL maliciosa desde la misma carpeta: **DLL sideloading**.

```bash
7z l sample.iso
7z x sample.iso -oextract/
file extract/*
cat extract/*.lnk | xxd | head
```

### 2. Cadena de ejecución

```bash
strings -n 6 extract/*.dll | head -40
```

Se buscan rutas de `AppData`, nombres de procesos de sistemas y cadenas de C2. En el LNK, el campo de argumentos revela qué binario legítimo se invoca y con qué parámetros.

### 3. Evasión

Los cargadores de esta familia suelen: comprobar el idioma/dominio del equipo, retrasar la ejecución con `Sleep`, y usar `CreateProcess` con línea de comandos ofuscada. Se documenta cada técnica con la evidencia que la soporta, no por parecido con otros casos.

### 4. Correlación con el host

`Amcache` da el hash y la ruta del binario ejecutado; `Prefetch` confirma que se lanzó y cuántas veces. Con eso se responde si hubo una segunda etapa descargada.

## Conclusiones

- Entrega por correo con contenedor + LNK y ejecución por DLL sideloading.
- Evasión basada en comprobaciones de entorno y retrasos, no en cifrado fuerte.
- Indicadores: nombres y hashes de los binarios, rutas de extracción y dominios de C2.

## Lecciones

- Los ISO/IMG se montan sin `Mark-of-the-Web` en su contenido: el usuario no ve la advertencia.
- El DLL sideloading abusa de un binario firmado; bloquear por firma no sirve, hay que mirar la ruta.
- Documentar la técnica con evidencia evita el error de atribuir la muestra a otra familia.
