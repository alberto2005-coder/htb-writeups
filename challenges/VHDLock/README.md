---
challenge: VHDLock
type: Hardware
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [hardware, vhdl, fpga, xor, simulation, ghdl]
---

# VHDLock — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El reto entrega un diseño VHDL que implementa una “cerradura”. Leyendo el flujo de datos se descubre una operación XOR con una constante y una comparación; simulando el circuito o invirtiendo la operación se obtiene la flag.

## Enunciado y superficie

- Hardware, Medium, retirado.
- Se entregan archivos `.vhd`, un testbench y posiblemente una captura.
- No hay servicio remoto.

```bash
ls
file *.vhd
```

## Reconocimiento

Se identifican las entidades y puertos: `clk`, `reset`, `data_in`, `data_out`, `valid`. El testbench aplica estímulos y muestra la salida.

```bash
ghdl -a *.vhd
ghdl -e tb_lock
ghdl -r tb_lock --vcd=lock.vcd
gtkwave lock.vcd
```

## Análisis

1. Se sigue `data_in` hasta el registro de salida.
2. Se localiza la operación XOR y la constante.
3. Se identifica la comparación con el valor esperado.
4. Se invierte la transformación (`cipher XOR key`) para recuperar ASCII.
5. Se valida la secuencia con el testbench.

```python
ct = bytes.fromhex('<ciphertext>')
key = b'<key>'
print(bytes(c ^ key[i % len(key)] for i, c in enumerate(ct)))
```

## Explicación del fallo

La “protección” es una transformación reversible sin secreto fuerte. El diseño y la clave están en el propio entregable, por lo que la simulación revela el flujo.

## Reproducción local

1. Compilar con GHDL.
2. Ejecutar el testbench y revisar ondas.
3. Extraer la constante XOR.
4. Decodificar el texto.
5. Comprobar el resultado.

## Evidencia

- Archivos VHDL y testbench.
- Captura de ondas.
- Script de decodificación y flag redactada.

## Lecciones aprendidas

- VHDL es código legible, no una caja negra.
- XOR con clave fija es reversible.
- GHDL/GTKWave permiten observar el flujo.
- La simulación es más rápida que sintetizar.

## Mitigación y detección

- No usar XOR con clave embebida como protección.
- Usar criptografía estándar y gestión de claves.
- Proteger el bitstream/diseño.
- Validar en hardware con autenticación.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/vhdlock/>
- <https://ghdl.github.io/ghdl/>
- <https://gtkwave.sourceforge.net/>
