---
sherlock: Ghost Thread
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, api-monitor, process-injection, shellcode]
---

# Ghost Thread — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un analista sospecha que el atacante inyectó código en un proceso legítimo para evitar rastros en disco. Se entrega una captura de API Monitor y una base de IDA del inyector; hay que identificar la técnica, las llamadas y el proceso objetivo.

## Evidencias

- `capture.apmx64` y su directorio de datos.
- `inject.exe.i64` para IDA.
- Descripción del incidente y preguntas guía.

```bash
unzip capture.apmx64 -d capture
find capture -maxdepth 3 -type f
```

## Investigación

### 1. Inventario

La captura es un ZIP con `log/monitoring.txt` y los datos crudos de cada llamada. Se conserva una copia y se documenta el hash antes de abrirla.

```bash
sha256sum capture.apmx64 inject.exe.i64
```

### 2. Llamadas Win32

Se buscan las APIs de inyección: snapshot de procesos, apertura del proceso, reserva de memoria, escritura y creación de un hilo remoto. El orden y los argumentos identifican la variante.

```text
CreateToolhelp32Snapshot -> Process32First/Next -> OpenProcess
VirtualAllocEx -> WriteProcessMemory -> CreateRemoteThread
```

### 3. Proceso y payload

El nombre del proceso objetivo se obtiene de la comparación en el inyector y del `PID` de la llamada. En IDA se revisa la función que se ejecuta antes de `main` y el tamaño del shellcode.

## Conclusiones

- La secuencia corresponde a inyección clásica con hilo remoto.
- El proceso objetivo es un editor legítimo, no un servicio del sistema.
- El payload se ejecuta en memoria y evita el disco.
- La captura de API Monitor es suficiente para reconstruir la cadena.

## Lecciones

- API Monitor permite ver llamadas sin ejecutar la muestra.
- El orden de las APIs es tan importante como sus nombres.
- Un proceso legítimo puede ocultar código malicioso.
- IDA complementa la captura para el tamaño y el origen del shellcode.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex>
- <https://attack.mitre.org/techniques/T1055/002/>
