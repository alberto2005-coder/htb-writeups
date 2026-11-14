---
sherlock: CAMouflage
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, kape, prefetch, mft, usn]
---

# CAMouflage — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una estación Windows muestra ejecutables con nombres de utilidades legítimas. Se sospecha que un instalador camuflado se ejecutó y dejó persistencia; se entrega una colección KAPE.

## Evidencias

- `Prefetch`, `Amcache.hve` y `SRUM`.
- `$MFT`, `$J` y `AppCompatCache`.
- Carpetas de usuario y descargas.

```bash
sha256sum evidence/* 2>/dev/null | head
find evidence -maxdepth 2 -type d
```

## Investigación

### 1. Triaje de ejecución

`PECmd` lista ejecutables y sus tiempos. Los nombres parecidos a herramientas conocidas se comparan con la ruta y el hash; un binario en `%TEMP%` o `Downloads` es sospechoso.

```bash
PECmd.exe -d evidence/Prefetch --csv prefetch
```

### 2. Correlación de creación

`MFTECmd` reconstruye la creación y modificación de archivos. `Amcache` aporta el primer avistamiento y el SHA-1; `SRUM` confirma consumo de red o CPU.

```bash
MFTECmd.exe -f '$MFT' --csv mft
```

### 3. Persistencia y alcance

Se revisan Run keys, tareas y servicios. La ruta del ejecutable se cruza con el prefetch y con el USN para saber si se copió, renombró o ejecutó varias veces.

## Conclusiones

- El nombre del archivo no identifica la herramienta.
- Prefetch, Amcache y MFT confirman ejecución y origen.
- La persistencia se valida con el registro y las tareas.

## Lecciones

- El camuflaje se detecta por ruta, firma y hash.
- Los artefactos de ejecución tienen vigencias distintas.
- La MFT ayuda a reconstruir copias y renombrados.
- Hay que separar instalación de ejecución.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman/PECmd>
- <https://attack.mitre.org/techniques/T1036/005/>
