---
topic: "Modbus/TCP en capturas: registros, funciones y extracción"
tags: [ics, modbus, pcap, tshark, plc, scada]
---

# Modbus/TCP en capturas: registros, funciones y extracción

[🇬🇧 English](modbus-pcap.en.md) | **Español**

> Nota reutilizable. Sin flags ni datos de una instancia concreta.

## Idea

Modbus es un protocolo de campo sin autenticación ni cifrado. En Modbus/TCP cada petición lleva una cabecera MBAP y una PDU con un **código de función**; el análisis de una captura consiste en separar tres cosas que se confunden con facilidad: el esclavo (`unit id`), la dirección (`reference number`) y el contenido (`register value`).

Esa distinción es la que resuelve retos como Watch Tower: la información puede estar en las direcciones y no en los valores.

## Modelo de datos

| Bloque | Tipo | Acceso maestro | Dirección típica |
|---|---|---|---|
| Coils | Booleano | Lectura/escritura | 0xxxx |
| Discrete inputs | Booleano | Solo lectura | 1xxxx |
| Input registers | 16 bits | Solo lectura | 3xxxx |
| Holding registers | 16 bits | Lectura/escritura | 4xxxx |

Cada bloque tiene hasta 65.536 elementos. En Wireshark las direcciones aparecen base 0; en documentación de PLC es habitual verlas base 1 (40001 = registro 0).

## Códigos de función

| Código | Función | Uso en análisis |
|---:|---|---|
| 1 | Read Coils | Comprobar estados binarios |
| 2 | Read Discrete Inputs | Sensores |
| 3 | Read Holding Registers | Extraer datos |
| 4 | Read Input Registers | Sensores analógicos |
| 5 | Write Single Coil | Accionar una válvula o relé (`FF 00` = ON) |
| 6 | Write Single Register | Cambiar un setpoint |
| 15 | Write Multiple Coils | Varios bits de una vez |
| 16 | Write Multiple Registers | Varios registros; aquí suele estar el payload |

## Cabecera MBAP

Transaction id (2) · protocol id (2, cero para Modbus) · length (2) · unit id (1). La PDU va después: función + datos. El transaction id empareja petición y respuesta; el `unit id` elige el esclavo cuando hay pasarela.

## Cómo se analiza

```bash
# protocolos presentes
tshark -r captura.pcapng -q -z io,phs

# funciones usadas y quién habla
tshark -r captura.pcapng -T fields -e ip.src -e modbus.func_code | sort | uniq -c

# direcciones de las escrituras de registros
tshark -r captura.pcapng -T fields \
  -Y 'modbus.func_code == 16' -e modbus.reference_num

# contenido escrito
tshark -r captura.pcapng -T fields \
  -Y 'modbus.func_code == 16' -e modbus.regval_uint16
```

Para convertir una secuencia de bytes o palabras a texto:

```bash
tshark -r captura.pcapng -T fields -Y 'modbus.func_code == 16' \
  -e modbus.reference_num | awk '{for (i = 1; i <= NF; i++) printf "%c", $i}'
```

## La trampa: dirección contra valor

- `modbus.reference_num` es el registro de inicio.
- `modbus.regval_uint16` es el contenido escrito o leído.
- `modbus.bitval` son los bits de coils y discrete inputs.

Si el texto no sale con los valores, probar con las direcciones (y al revés). Un registro por carácter es la convención habitual; los valores no imprimibles suelen indicar que se está leyendo el bloque equivocado.

## Leer y escribir desde Python

```python
from pymodbus.client import ModbusTcpClient

c = ModbusTcpClient("127.0.0.1", port=502)
c.connect()
rr = c.read_holding_registers(0, count=8, slave=52)
print(rr.registers)
c.write_coil(5, True, slave=52)
c.close()
```

`slave=` es el `unit id`; en versiones nuevas de pymodbus el parámetro puede llamarse `device_id`. Para RTU, `ModbusSerialClient` con puerto, baudios, paridad y bits de parada.

## Detección

- Tráfico Modbus desde hosts que no son el SCADA o el ingeniero.
- Escrituras a coils de válvulas, bombas o interlocks.
- Secuencias de direcciones crecientes (canal encubierto) y lecturas masivas.
- Cambios auto→manual y comandos fuera de ventana de mantenimiento.

MITRE ATT&CK for ICS: T0836 (Modify Parameter), T0855 (Unauthorized Command Message) y T0842 (Network Sniffing).

## Referencias

- <https://modbus.org/specs.php>
- <https://www.wireshark.org/docs/dfref/m/modbus.html>
- <https://pymodbus.readthedocs.io/>
