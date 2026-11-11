---
challenge: Intrusion
category: Challenge
type: ICS
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ics, scada, modbus, pcap, umodbus, plc]
---

# Intrusion — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Captura Modbus de una intrusión más una planta viva a la que conectarse. La captura da los números de registro que el atacante consultó y el `unit id` (52); la segunda parte consiste en leer esos holding registers en orden contra la instancia y reconstruir la flag. El análisis puro no basta: hay que hablar Modbus.

## Enunciado y superficie

- Categoría **ICS**, dificultad **Easy**; Business CTF 2023.
- Se entrega `ics_intrusion.zip` con `network_logs.pcapng` y una instancia Docker con la planta Modbus.
- El escenario: tras acceder a la infraestructura enemiga se capturó tráfico de su red Modbus; hay que localizar los registros con la información sensible y extraerla.

## Reconocimiento

- La captura es Modbus/TCP contra el puerto 502.
- El `unit id` que aparece en las peticiones es **52**.
- Los `reference numbers` de las lecturas apuntan a los holding registers de interés.

La instancia expone un PLC simulado; el cliente se conecta a `127.0.0.1:502` desde la propia máquina del reto.

## Análisis del código

No hay binario, pero sí una lógica de escalera descrita en el PDF: los registros no son independientes, representan válvulas, sensores y estados. La captura muestra qué direcciones tocó el atacante y en qué orden.

La flag se reconstruye leyendo esos registros en el orden de la captura y pasando cada valor de 16 bits a carácter. Un registro por carácter es la convención habitual en estos retos; si el valor no es imprimible, hay que revisar si se está leyendo el registro correcto o si el dato está en el byte alto.

## Explicación del fallo

El PLC acepta lecturas sin autenticación desde cualquier host con conectividad al puerto 502. El atacante no explota un CVE: usa el protocolo tal y como está diseñado. La lección es que la superficie OT suele confiar en la segmentación de red, no en autenticación.

## Reproducción local

Con la instancia arrancada, un cliente mínimo con `umodbus` o `pymodbus`:

```python
from pymodbus.client import ModbusTcpClient

c = ModbusTcpClient("127.0.0.1", port=502)
c.connect()
out = []
for addr in registros:              # extraídos del PCAP, en orden
    rr = c.read_holding_registers(addr, count=1, slave=52)
    out.append(chr(rr.registers[0]))
print("".join(out))
c.close()
```

Los `registros` se obtienen de la captura:

```bash
tshark -r network_logs.pcapng -T fields \
  -Y 'modbus.func_code == 3' -e modbus.reference_num | tr ',' '\n' | sort -n -u
```

## Explotación

1. Extraer del PCAP los `reference numbers` de las lecturas y ordenarlos.
2. Confirmar el `unit id` 52.
3. Leer cada registro contra la instancia.
4. Convertir a ASCII y enviar la flag.

## Evidencia

- Lectura de registros con valores imprimibles que forman `HTB{...}`.
- Flag recortada en esta ficha.

## Lecciones aprendidas

- En Modbus, `unit id` y dirección son parte de la petición; equivocar uno devuelve excepción o datos de otro esclavo.
- La captura dice *qué* leer; la instancia da el *valor actual*. Sin las dos partes no hay flag.
- Automatizar la lectura evita 30 peticiones a mano y errores de orden.

## Mitigaciones y detección

- Restringir el puerto 502 a los maestros conocidos y segmentar IT/OT.
- Detección: lecturas masivas y secuenciales de holding registers, conexiones nuevas al PLC y tráfico Modbus desde estaciones de trabajo.
- MITRE ATT&CK for ICS: T0846 (Remote System Discovery) y T0836 (Modify Parameter) como contexto.

## Referencias

- <https://www.hackthebox.com/challenges/intrusion>
- <https://www.matthewdfurtado.com/blog/scada-intrusion>
- <https://medium.com/@biero-llagas/htb-ics-tracks-write-up-factory-watch-tower-and-intrusion-13065c1b0e93>
