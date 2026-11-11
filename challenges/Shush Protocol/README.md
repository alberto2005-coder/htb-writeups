---
challenge: Shush Protocol
category: Challenge
type: ics
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [ics, modbus, pcap, wireshark, custom-function-code]
---

# Shush Protocol — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Un PCAP de Modbus/TCP donde el dispositivo de control habla un protocolo propietario con el **código de función 102**, que no existe en el estándar. Siguiendo el flujo TCP de esos paquetes y mirando el volcado en hexadecimal aparece el usuario `operator` y su contraseña, que es la flag. No hay que explotar nada: hay que leer el tráfico.

## Enunciado y superficie

- Categoría **ICS**, dificultad **Very Easy**; Business CTF 2024.
- Se entrega `ics_shush_protocol.zip`, que contiene `traffic.pcapng`.
- El objetivo es la contraseña que el dispositivo de control usa para hablar con el PLC.

## Reconocimiento

- Todo el tráfico es Modbus/TCP contra el puerto 502.
- La mayoría de paquetes usan funciones estándar, pero varios llevan la función **102**: un código propietario.
- Casi todos esos paquetes son ruido de diagnóstico; uno solo transporta una cantidad de datos anómala.

## Análisis del código

No hay binario ni instancia. El "código" es el protocolo: la función 102 encapsula sus propios campos dentro de la PDU de Modbus. Al seguir el flujo TCP y cambiar la vista a `Hex Dump`, se ve que el paquete grande escribe una cadena con el usuario y la contraseña en claro dentro de los datos.

La función 102 no aparece en la tabla de funciones de Modbus, así que Wireshark no la disecciona: hay que leer los bytes.

## Explicación del fallo

El protocolo propietario no aporta seguridad: la contraseña viaja sin cifrar y el cliente la envía al PLC en cada sesión. La oscuridad del código de función no protege el dato, y una captura pasiva basta para extraerlo.

## Reproducción local

```bash
# localizar los paquetes con la función propietaria
tshark -r traffic.pcapng -Y 'modbus.func_code == 102' -T fields -e data

# o abrir el flujo TCP en Wireshark: Follow → TCP Stream → Show data as Hex Dump
```

El volcado en hexadecimal se convierte a texto con `xxd -r -p` o con la operación `From Hex` de CyberChef.

## Explotación

1. Abrir la captura y filtrar `modbus.func_code == 102`.
2. Seguir el flujo TCP del paquete con más datos.
3. Cambiar la vista a hexadecimal y decodificar a ASCII.
4. Enviar la contraseña encontrada.

## Evidencia

- El volcado muestra el usuario `operator` seguido de la contraseña con formato de flag.
- Flag recortada en esta ficha.

## Lecciones aprendidas

- Los códigos de función por encima de los estándar suelen indicar protocolos propietarios.
- Un solo paquete anómalo puede contener toda la información; conviene ordenar por longitud.
- Seguir el flujo TCP es más fiable que leer paquetes sueltos cuando la PDU está fragmentada.
- "Protocolo propietario" no significa "cifrado".

## Mitigaciones y detección

- No enviar credenciales en claro: autenticación mutua y túneles en el segmento OT.
- Detección: códigos de función no estándar, escrituras grandes desde un host de diagnóstico y conexiones nuevas al PLC.
- MITRE ATT&CK for ICS: T0842 (Network Sniffing) y T0836 (Modify Parameter) como contexto.

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/ics/Shush%20Protocol%20%5BVery%20Easy%5D>
- <https://www.matthewdfurtado.com/blog/ics_shushprotocol/>
- <https://medium.com/@a19941006/htb-ctf-shush-protocol-9c134bd8ea13>
