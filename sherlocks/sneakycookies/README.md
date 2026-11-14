---
sherlock: SneakyCookies
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, lnk, phishing, srum, evtx]
---

# SneakyCookies — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un usuario de una empresa recibe un correo con un supuesto PDF. El filtro de correo estaba en mantenimiento y el archivo se abrió. Se entrega un triaje del perfil de usuario y registros del sistema para reconstruir el compromiso.

## Evidencias

- `TRIAGE-L3-BELLS` con el perfil de `Bingle Jollybeard`.
- `christmas_slab.pdf.lnk`.
- EVTX, SRUM y archivos de `%TEMP%`.

```bash
sha256sum christmas_slab.pdf.lnk
LECmd.exe -f christmas_slab.pdf.lnk
```

## Investigación

### 1. Inventario y triaje

`LECmd` muestra que el LNK apunta a `ssh.exe` con argumentos que descargan un ejecutable desde un host externo. El nombre del archivo simula un PDF. Se revisan descargas, prefetch y procesos hijos.

```bash
LECmd.exe -f christmas_slab.pdf.lnk --csv out
```

### 2. Línea temporal

El LNK se ejecuta desde `Downloads`; `ssh.exe` usa `-o PermitLocalCommand=yes` y `LocalCommand` para copiar y lanzar un binario. Después aparecen conexiones al C2 y creación de una cuenta local. Los EVTX y SRUM confirman los tiempos.

```bash
EvtxECmd.exe -d C/Windows/System32/winevt/Logs --csv evtx
SrumECmd.exe -d C/Windows/System32/SRU --csv srum
```

### 3. Artefacto clave

El flujo de SRUM muestra el tráfico del ejecutable y el volumen enviado. La cuenta creada se añade a administradores locales. El nombre del binario y el host de C2 son los IOC principales.

## Conclusiones

- El acceso inicial fue un LNK disfrazado de PDF.
- `ssh.exe` se usó como LOLBin para descargar y ejecutar.
- El atacante creó persistencia con una cuenta local.
- Hay que rotar credenciales y revisar otros perfiles.

## Lecciones

- Los LNK se analizan con `LECmd`, no solo con `strings`.
- `ssh.exe` puede ejecutar comandos locales.
- SRUM aporta evidencia de red y uso de recursos.
- Un filtro de correo caído no debe detener la monitorización.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/luckystars0612/Sherlock-HTB/tree/main/SneakyCookies>
- <https://attack.mitre.org/techniques/T1204/002/>
