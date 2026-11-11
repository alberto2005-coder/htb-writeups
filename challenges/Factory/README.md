---
challenge: Factory
category: Challenge
type: ics
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ics, scada, modbus, rtu, plc, ladder-logic]
---

# Factory — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Planta de agua con la HMI caída y el PLC en *halt* porque los sensores de nivel están corruptos. Hay que entender el diagrama de lógica de escalera, pasar el PLC a modo manual y forzar la válvula de salida para vaciar el tanque antes de que desborde. Se hace con Modbus RTU sobre la red serie a la que da acceso el operativo, no con un exploit.

## Enunciado y superficie

- Categoría **ICS**, dificultad **Easy**; Business CTF 2023.
- Se entrega un PDF con la planta remota y el mapa de la red Modbus RTU, además de la conexión a la instancia.
- El PLC tiene un esclavo en la red serie; la HMI ya no responde.

## Reconocimiento

- Identificar el esclavo y el medio: Modbus RTU sobre serie, con la pasarela que indica el PDF.
- Leer el diagrama: qué coil abre la válvula de entrada, cuál la de salida, cuál activa el modo manual y cuál el arranque.
- Comprobar el estado: `auto_mode` activo y el PLC en *halt* por los sensores de nivel corruptos.

## Análisis del código

La lógica de escalera del PDF es el "código". En ella se ve que el PLC solo actúa sobre las válvulas si está en manual; en automático, los sensores corruptos mantienen el *halt*. La secuencia es:

1. Desactivar el modo automático.
2. Activar el modo manual.
3. Abrir la válvula de salida (y cerrar la de entrada) con `Write Single Coil` (función 5).
4. Confirmar con lecturas de coils que el tanque se vacía.

El esclavo del ejemplo es el 52 y la válvula de salida se fuerza con `FF 00` en su coil, según el mapa del PDF.

## Explicación del fallo

No hay CVE: el PLC acepta escrituras de coils sin autenticación desde la red de campo, y la lógica de seguridad depende de que los sensores sean fiables. El reto demuestra el impacto físico de un `Write Single Coil`: no se exfiltra un dato, se mueve una válvula.

## Reproducción local

Con `mbpoll` contra la pasarela serie (ajustar dispositivo y velocidad a los del PDF):

```bash
mbpoll -m rtu -a 52 -b 9600 -P none -d 8 -s 1 -t 0 -r 5 /dev/ttyUSB0 0   # auto_mode off
mbpoll -m rtu -a 52 -b 9600 -P none -d 8 -s 1 -t 0 -r 6 /dev/ttyUSB0 1   # manual on
mbpoll -m rtu -a 52 -b 9600 -P none -d 8 -s 1 -t 0 -r 5 /dev/ttyUSB0 1   # salida abierta
```

Los números de coil son los del mapa del PDF; no se copian aquí porque cambian con la instancia.

## Explotación

1. Leer el diagrama y localizar los coils de modo y válvulas.
2. Escribir `auto_mode = 0` y `manual_mode = 1`.
3. Forzar la válvula de salida y cerrar la de entrada.
4. Leer el estado hasta que el tanque quede vacío; la plataforma valida y devuelve la flag.

## Evidencia

- Coils de modo y válvula con los valores esperados tras la secuencia.
- Flag recortada en esta ficha.

## Lecciones aprendidas

- En ICS, el objetivo puede ser físico: vaciar un tanque, no leer un fichero.
- La lógica de escalera es la especificación; sin leerla, escribir coils es adivinar.
- `Write Single Coil` usa `FF 00` para ON y `00 00` para OFF.
- Modbus RTU necesita parámetros de puerto correctos (baudios, paridad, bits de parada) antes de cualquier escritura.

## Mitigaciones y detección

- Modo manual protegido por enclavamientos físicos y autenticación en la pasarela.
- Detección: cambios de modo automático→manual, escrituras en coils de válvulas y comandos desde hosts fuera del SCADA.
- MITRE ATT&CK for ICS: T0836 (Modify Parameter) y T0855 (Unauthorized Command Message).

## Referencias

- <https://www.hackthebox.com/challenges/factory>
- <https://piyushs3v3n.github.io/HackTheBox-Factory-WriteUp>
- <https://medium.com/@biero-llagas/htb-ics-tracks-write-up-factory-watch-tower-and-intrusion-13065c1b0e93>
- <https://foobarto.me/htb/challenges>
