---
sherlock: Trojan
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, prefetch, memory, pcap, malware]
---

# Trojan — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un equipo Windows presenta conexiones salientes tras la ejecución de un supuesto instalador. Se entrega una imagen de disco, un volcado de memoria y una captura de red.

## Evidencias

- `Prefetch`, `Amcache` y `$MFT`.
- `memory.raw` y `capture.pcap`.
- Directorio de usuario y descargas.

```bash
sha256sum evidence/*
vol3 -f memory.raw windows.info
```

## Investigación

### 1. Ejecución en disco

`PECmd` confirma el instalador y sus procesos hijos. La ruta y el hash se comparan con firmas legítimas; `MFTECmd` muestra cuándo llegó el archivo.

```bash
PECmd.exe -d Prefetch --csv prefetch
```

### 2. Memoria

Volatility 3 enumera procesos, conexiones y módulos. Un proceso con nombre legítimo pero ruta anómala o un módulo no firmado es el punto de partida.

```bash
vol3 -f memory.raw windows.pslist
vol3 -f memory.raw windows.netscan
```

### 3. Red

Se filtran conexiones al exterior y se extraen dominios, JA3 y HTTP. El destino se cruza con el proceso y con el momento de ejecución para separar ruido de C2.

```bash
tshark -r capture.pcap -Y 'dns or tls.handshake'
```

## Conclusiones

- El instalador ejecutó un proceso hijo no esperado.
- La memoria confirma el proceso y su conexión.
- El PCAP identifica el destino del C2.
- La ruta y el hash permiten buscar el binario.

## Lecciones

- Disco, memoria y red responden preguntas distintas.
- El nombre del proceso no es prueba suficiente.
- Volatility necesita el perfil correcto para Windows.
- La correlación temporal evita falsos positivos.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/volatilityfoundation/volatility3>
- <https://attack.mitre.org/techniques/T1204/002/>
