---
challenge: Unique
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, can-bus, saleae, logic-analyzer, automotive]
---

# Unique — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se captura una señal diferencial de un vehículo en un archivo Saleae `.sal`. La velocidad no es serie asíncrona estándar: es CAN a 125 kbps. Al decodificar las tramas, el VIN y la flag aparecen en los bytes de datos.

## Enunciado y superficie

- Hardware, Easy, retirado.
- Se entrega `trace_captured.sal`.
- El objetivo es recuperar el VIN que el vehículo transmite repetidamente.

```bash
file trace_captured.sal
7z l trace_captured.sal
```

## Reconocimiento

- El `.sal` es un contenedor comprimido con señales digitales y metadatos.
- Hay dos señales complementarias, compatibles con CAN_H y CAN_L.
- La decodificación como UART no produce caracteres coherentes.

```bash
unzip -l trace_captured.sal
```

## Análisis

1. Abrir la captura en Saleae Logic 2.
2. Medir el periodo de bit: alrededor de 8 µs.
3. Calcular `1 / 8 µs ≈ 125 kbps`.
4. Añadir el analizador CAN con 125000 bit/s.
5. Exportar las tramas y buscar ASCII en el campo de datos.

```text
bitrate = 1 / bit_time
125000 ≈ 1 / 8e-6
```

## Explicación del fallo

No hay una vulnerabilidad de software: el reto demuestra que una captura física mal interpretada oculta información. El protocolo correcto es CAN, no UART; la velocidad debe deducirse de la señal y no asumirse.

## Reproducción local

- Instalar Logic 2 y el analizador CAN.
- Cargar el `.sal` y seleccionar los canales diferenciales.
- Probar 125000, 250000 y 500000 bit/s.
- Exportar a CSV y filtrar bytes imprimibles.

```bash
# Tras exportar el CSV
python3 - <<'PY'
import csv
for row in csv.reader(open("can.csv")):
    print("".join(chr(int(x, 16)) for x in row if 32 <= int(x, 16) < 127))
PY
```

## Evidencia

- Medición del periodo de bit.
- Configuración del analizador CAN.
- Tramas con el VIN y la flag, redactados.

## Lecciones aprendidas

- La capa física determina qué analizador tiene sentido.
- Una velocidad incorrecta produce datos plausibles pero falsos.
- Los archivos `.sal` son inspeccionables sin la interfaz gráfica.

## Mitigaciones y detección

- Segmentar y monitorizar la red CAN de vehículos.
- No confiar en el VIN como autenticación.
- Registrar tramas anómalas y accesos al bus OBD-II.
- Proteger la captura y los metadatos del dispositivo.

## Referencias

- <https://www.hackthebox.com/challenges/Unique>
- <https://www.saleae.com/downloads/>
- <https://en.wikipedia.org/wiki/CAN_bus>
