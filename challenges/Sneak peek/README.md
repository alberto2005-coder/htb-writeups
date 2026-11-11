---
challenge: Sneak peek
category: Challenge
type: ics
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ics, modbus, custom-protocol, pymodbus, md5, plc]
---

# Sneak peek — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

PLC con un protocolo propietario sobre Modbus/TCP (función `0x64`) que ofrece tres comandos: leer memoria (`0x20`), escribir memoria (`0x21`) y obtener el secreto (`0x22`). Solo el último pide contraseña, y su hash MD5 vive en un bloque de memoria **escribible sin autenticación**. La solución es leer el bloque, localizar el hash, sustituirlo por el MD5 de una contraseña conocida y pedir el secreto.

## Enunciado y superficie

- Categoría **ICS**, dificultad **Easy**; Business CTF 2024.
- Instancia online más un archivo con `protocol_information.png` y `client.py` (envoltorios de `ModbusRequest`/`ModbusResponse`).
- La pista del enunciado: la contraseña está en el bloque de memoria como un hash MD5 "incrackeable".

## Reconocimiento

La imagen del protocolo documenta:

| Comando | Código | Datos | Respuesta |
|---|---:|---|---|
| `read_memory_block` | `0x20` | `addr[3] + length` | bytes leídos |
| `write_memory_block` | `0x21` | `addr[3] + datos` | `[1]` si completa |
| `get_secret` | `0x22` | contraseña en claro | secreto (la flag) |

- Bloque de memoria de 16 KiB; `length` es un solo byte, así que se lee como máximo 256 bytes por petición.
- Código de error `0xE009`: contraseña inválida.
- Solo `get_secret` valida contraseña; lectura y escritura van sin autenticación.

## Análisis del código

`client.py` registra una clase de respuesta para la función `0x64` en el framer de pymodbus; el `encode`/`decode` es un `struct.pack` de session, code y datos. Con eso se pueden enviar los tres comandos.

El fallo está en el modelo de confianza: la comprobación de contraseña consiste en comparar el MD5 recibido con el que está almacenado en memoria, pero ese bloque se escribe con `0x21` sin comprobar nada. Cambiar el hash por el de una contraseña propia equivale a cambiar la contraseña.

## Explicación del fallo

Autorización basada en un dato que el propio cliente puede modificar. No hay autenticación en `write_memory_block` ni protección de la región donde vive el hash. Es un caso de **integridad de los datos de autenticación**: si el atacante puede escribirlos, la comprobación deja de valer.

## Reproducción local

```python
from pymodbus.client import ModbusTcpClient
from pymodbus.transaction import ModbusSocketFramer
import hashlib

client = ModbusTcpClient(HOST, port=PORT, framer=ModbusSocketFramer)
client.framer.decoder.register(CustomProtocolResponse)   # clase del client.py

# 1) leer los 16 KiB en bloques de 255 bytes y concatenar
# 2) localizar la entrada de 16 bytes (hash) y su índice
# 3) escribir el MD5 de "new_password" en índice+offset, offset 0..5
# 4) get_secret con "new_password"
client.write...  # sustituido por send_packet(client, SESSION, 0x21, addr + md5_bytes)
```

El índice de la entrada y los cinco bytes que la acompañan cambian con la instancia; por eso el solver prueba los seis desplazamientos hasta que `get_secret` deja de devolver `0xE009`.

## Explotación

1. Leer el bloque de memoria completo (64 lecturas de 255 bytes; parar al recibir `0xFF`).
2. Separar entradas por el byte `0x00` y quedarse con la de 16 bytes: es el MD5.
3. Calcular el MD5 de una contraseña conocida y sobrescribir la entrada.
4. Llamar a `0x22` con esa contraseña; la respuesta son los bytes ASCII de la flag.

## Evidencia

- `write_memory_block` responde `[1]` y `get_secret` deja de devolver el error `0xE009`.
- La respuesta contiene una secuencia ASCII con formato de flag.
- Flag recortada en esta ficha.

## Lecciones aprendidas

- Un protocolo propietario sobre Modbus se analiza leyendo su documentación y sus códigos, no adivinando.
- Los comandos de lectura/escritura sin autenticación convierten cualquier control de acceso en decorativo.
- Los límites de tamaño (un byte de longitud) obligan a iterar y a llevar la cuenta de la dirección.
- Probar desplazamientos alrededor de una entrada encontrada es más rápido que entender cada byte de relleno.

## Mitigaciones y detección

- Proteger la región de credenciales contra escritura y autenticar cualquier `write_memory_block`.
- No derivar autorización de un hash almacenado en memoria de proceso accesible por red.
- Detección: escrituras en direcciones de configuración, uso de códigos de función no estándar y lecturas secuenciales de todo el bloque.
- MITRE ATT&CK for ICS: T0836 (Modify Parameter) y T0855 (Unauthorized Command Message).

## Referencias

- <https://github.com/hackthebox/business-ctf-2024/tree/main/ics/Sneak%20peek%20%5BEasy%5D>
- <https://github.com/hackthebox/business-ctf-2024>
- <https://pymodbus.readthedocs.io/>
