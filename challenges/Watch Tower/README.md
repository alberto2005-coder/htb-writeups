---
challenge: Watch Tower
category: Challenge
type: ICS
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [ics, scada, modbus, pcap, tshark]
---

# Watch Tower — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Reto de análisis de tráfico: un `pcapng` con Modbus/TCP en el que alguien escribió datos en un esclavo. La flag no está en los valores escritos, sino en los **números de referencia** de los `Write Multiple Registers` (función 16): convertidos a ASCII, deletrean `HTB{...}`. Se resuelve con un filtro de `tshark` y un `awk`.

## Enunciado y superficie

- Categoría **ICS** (también aparece como Hardware/SCADA), dificultad **Very Easy**.
- Business CTF 2023; se entrega `ics_watch_tower.zip`, que contiene `tower_logs.pcapng`.
- No hay servicio que atacar: todo el trabajo es sobre la captura.

## Reconocimiento

`Statistics → Protocol Hierarchy` muestra únicamente Modbus/TCP. Los códigos de función presentes son:

| Código | Función | Papel en la captura |
|---:|---|---|
| 1 | Read Coils | Lecturas de comprobación |
| 15 | Write Multiple Coils | Escritura inicial de coils (sin ASCII útil) |
| 16 | Write Multiple Registers | 57 escrituras: aquí está el dato |

El maestro es `192.168.1.150`; el esclavo responde desde el puerto 502.

## Análisis del código

No hay binario. En Modbus/TCP cada PDU va precedida por la cabecera MBAP (transaction id, protocol id, longitud, unit id) y la función 16 incluye:

- **Reference Number**: registro de inicio de la escritura.
- **Word Count** y **Register Value**: cuántos registros y qué valores.

En esta captura los valores son ruido, pero los `reference numbers` van 72, 84, 66, 123… que en ASCII son `H`, `T`, `B`, `{`. La flag está en la aritmética de direcciones, no en el contenido.

## Explicación del fallo

El escenario dice que el atacante "recopiló y alteró" información. La alteración está en las direcciones: usar el número de registro como canal encubierto permite escribir datos sin que el valor write parezca sospechoso. Es un caso de **metadata como canal**, no de un fallo de protocolo.

## Reproducción local

```bash
tshark -r tower_logs.pcapng -T fields \
  -Y 'ip.src == 192.168.1.150 && modbus.func_code == 16' \
  -e modbus.reference_num \
  | awk '{for (i = 1; i <= NF; i++) printf "%c", $i}'
```

Variante con Wireshark: filtro `modbus.func_code == 16`, columna `modbus.reference_num` y `File → Export Packet Dissections`.

## Explotación

1. Abrir la captura y confirmar que solo hay Modbus/TCP.
2. Filtrar función 16 y origen del maestro.
3. Extraer `modbus.reference_num` y convertirlo a ASCII.
4. Enviar la cadena resultante.

## Evidencia

- La secuencia decodificada empieza por el prefijo de flag y termina en la llave de cierre.
- Flag recortada en esta ficha.

## Lecciones aprendidas

- En Modbus, dirección y valor son dos campos distintos; mirar solo el valor deja fuera la mitad del tráfico.
- `modbus.reference_num` (registro) no es `modbus.regval_uint16` (contenido).
- `tshark -T fields` convierte una captura en una tabla procesable con herramientas de shell.
- Un canal encubierto puede usar direcciones, tiempos o tamaños, no solo payloads.

## Mitigaciones y detección

- Modbus/TCP no tiene autenticación ni cifrado: la defensa es segmentación, listas blancas de maestros y monitorización pasiva del puerto 502.
- Detección: escrituras a registros fuera del mapa habitual, secuencias de direcciones crecientes y tráfico Modbus desde hosts que no son el SCADA.
- MITRE ATT&CK for ICS: T0836 (Modify Parameter) y T0842 (Network Sniffing) como contexto.

## Referencias

- <https://www.hackthebox.com/challenges/watch-tower>
- <https://7rocky.github.io/en/ctf/htb-challenges/ics/watch-tower/>
- <https://www.matthewdfurtado.com/blog/scada-watchtower>
- <https://sud0ru.ghost.io/ics-security-series-part-1>
