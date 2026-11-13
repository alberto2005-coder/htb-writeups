---
topic: CAN bus
tags: [hardware, automotive, can, logic-analyzer, saleae]
---

# CAN bus

[🌐 English](can-bus.en.md) | **Español**

## Concepto

Controller Area Network (CAN) es un bus diferencial usado en vehículos y sistemas industriales. Los nodos comparten un par de señales, CAN_H y CAN_L, y transmiten tramas con un identificador y hasta ocho bytes de datos. La velocidad más común en automoción es 500 kbps, aunque también se usan 125 y 250 kbps.

## Cuándo aplica

- Análisis de capturas de un analizador lógico.
- Diagnóstico de un vehículo o de una red de control.
- Retos con archivos `.sal`, `.csv` o trazas de bus.
- Investigación de manipulación de mensajes o sensores.

## Requisitos y condiciones

- Acceso físico o una captura de las señales diferenciales.
- Conocimiento de la velocidad de bit.
- Analizador CAN o decodificador que acepte el formato.
- Referencia del fabricante para interpretar identificadores y señales.

## Procedimiento

1. Abrir la captura en un analizador lógico.
2. Medir el periodo de bit y calcular la velocidad.
3. Configurar el analizador CAN con esa velocidad.
4. Exportar las tramas con identificador, longitud y datos.
5. Filtrar por identificador y buscar ASCII o señales conocidas.
6. Contrastar con la documentación del vehículo o del dispositivo.

```text
bitrate = 1 / bit_time
125000 ≈ 1 / 8e-6
```

## Variantes

- CAN clásico y CAN-FD.
- UDS sobre CAN para diagnóstico.
- OBD-II como interfaz de acceso.
- LIN, FlexRay y Ethernet automotriz en redes modernas.

## Limitaciones

- Una velocidad incorrecta produce datos plausibles pero falsos.
- Los identificadores y el significado de los bytes son específicos del fabricante.
- La captura no siempre incluye el contexto físico.
- El bus no está diseñado con autenticación ni confidencialidad.

## Mitigación

- Segmentar la red y usar gateways entre dominios.
- Autenticar mensajes críticos cuando el estándar lo permita.
- Limitar el acceso al puerto OBD-II.
- Monitorizar identificadores y frecuencias anómalas.

## Detección

- Alertar de tramas con identificadores desconocidos o frecuencias alteradas.
- Detectar inyección de mensajes y repetición.
- Correlacionar con eventos físicos y diagnósticos.
- Registrar accesos al bus y cambios de firmware.

## Referencias

- <https://en.wikipedia.org/wiki/CAN_bus>
- <https://www.saleae.com/downloads/>
- <https://attack.mitre.org/techniques/T1548/>
