---
topic: Modbus/TCP in captures: registers, functions and extraction
tags: [ics, modbus, pcap, tshark, plc, scada]
---

# Modbus/TCP in captures: registers, functions and extraction

**English** | [🇪🇸 Español](modbus-pcap.md)

> Reusable note. No flags or instance-specific data.

## Idea

Modbus is a field protocol with no authentication or encryption. In Modbus/TCP each request carries an MBAP header and a PDU with a **function code**; analysing a capture means separating three things that are easy to confuse: the slave (`unit id`), the address (`reference number`) and the content (`register value`).

That distinction is what solves challenges like Watch Tower: the information can sit in the addresses rather than the values.

## Data model

| Block | Type | Master access | Typical address |
|---|---|---|---|
| Coils | Boolean | Read/write | 0xxxx |
| Discrete inputs | Boolean | Read-only | 1xxxx |
| Input registers | 16-bit | Read-only | 3xxxx |
| Holding registers | 16-bit | Read/write | 4xxxx |

Each block holds up to 65,536 elements. Wireshark shows addresses zero-based; PLC documentation often uses one-based notation (40001 = register 0).

## Function codes

| Code | Function | Use in analysis |
|---:|---|---|
| 1 | Read Coils | Check binary states |
| 2 | Read Discrete Inputs | Sensors |
| 3 | Read Holding Registers | Extract data |
| 4 | Read Input Registers | Analogue sensors |
| 5 | Write Single Coil | Drive a valve or relay (`FF 00` = ON) |
| 6 | Write Single Register | Change a setpoint |
| 15 | Write Multiple Coils | Several bits at once |
| 16 | Write Multiple Registers | Several registers; the payload usually lives here |

## MBAP header

Transaction id (2) · protocol id (2, zero for Modbus) · length (2) · unit id (1). The PDU follows: function + data. The transaction id pairs request and response; the `unit id` selects the slave behind a gateway.

## How to analyse

```bash
# protocols present
tshark -r capture.pcapng -q -z io,phs

# functions used and who talks
tshark -r capture.pcapng -T fields -e ip.src -e modbus.func_code | sort | uniq -c

# addresses of register writes
tshark -r capture.pcapng -T fields \
  -Y 'modbus.func_code == 16' -e modbus.reference_num

# written content
tshark -r capture.pcapng -T fields \
  -Y 'modbus.func_code == 16' -e modbus.regval_uint16
```

Convert a byte or word sequence to text:

```bash
tshark -r capture.pcapng -T fields -Y 'modbus.func_code == 16' \
  -e modbus.reference_num | awk '{for (i = 1; i <= NF; i++) printf "%c", $i}'
```

## The trap: address versus value

- `modbus.reference_num` is the starting register.
- `modbus.regval_uint16` is the written or read content.
- `modbus.bitval` holds coil and discrete-input bits.

If the text does not appear in the values, try the addresses (and vice versa). One register per character is the usual convention; non-printable values usually mean the wrong block is being read.

## Reading and writing from Python

```python
from pymodbus.client import ModbusTcpClient

c = ModbusTcpClient("127.0.0.1", port=502)
c.connect()
rr = c.read_holding_registers(0, count=8, slave=52)
print(rr.registers)
c.write_coil(5, True, slave=52)
c.close()
```

`slave=` is the `unit id`; newer pymodbus releases may call the argument `device_id`. For RTU use `ModbusSerialClient` with port, baud rate, parity and stop bits.

## Detection

- Modbus traffic from hosts that are not the SCADA or the engineer.
- Writes to valve, pump or interlock coils.
- Ascending address sequences (covert channel) and bulk reads.
- Auto-to-manual transitions and commands outside maintenance windows.

MITRE ATT&CK for ICS: T0836 (Modify Parameter), T0855 (Unauthorized Command Message) and T0842 (Network Sniffing).

## References

- <https://modbus.org/specs.php>
- <https://www.wireshark.org/docs/dfref/m/modbus.html>
- <https://pymodbus.readthedocs.io/>
