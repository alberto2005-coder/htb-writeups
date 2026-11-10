---
challenge: Deadly Arthropod
category: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, usb, hid, pcap, keystrokes]
type: Forensics
---

# Deadly Arthropod — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

La captura es de tráfico **USB de un teclado** (la descripción del dispositivo lo identifica como **Razer BlackWidow Ultimate 2013**). Cada pulsación viaja como un informe HID de 8 bytes; filtrando los paquetes de 35 bytes y descartando los informes vacíos, la secuencia de *keycodes* da el texto tecleado, que contiene la flag. El detalle está en el mapa de teclas y en las mayúsculas.

## Enunciado y superficie

Se entrega `deadly_arthropod.pcap`, una captura de una sola transferencia USB sin tráfico de red. Categoría Forensics.

## Reconocimiento

```bash
tshark -r deadly_arthropod.pcap -q -z io,phs
```

Solo hay USB. Enumerando los dispositivos aparece un teclado; sus informes HID son los paquetes de **35 bytes** (los de 27 son el resto de la enumeración).

## Análisis del código

El informe HID de arranque tiene 8 bytes: el byte 0 son los modificadores (Shift) y el byte 2 el *keycode*. Los informes `00 00 ...` son liberaciones y hay que descartarlos, o cada tecla sale dos veces.

## Explicación del fallo

La captura contiene tráfico **USB de un teclado**. Cada pulsación viaja como un informe HID de 8 bytes; reconstruyendo la secuencia de *keycodes* se lee el texto que se tecleó, que es la flag. El detalle está en el mapa de teclas y en las mayúsculas.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Una captura de tráfico USB (`usb.pcapng`).

## Lecciones aprendidas

- **Informes vacíos**: si no se filtran, cada tecla aparece dos veces (pulsación y liberación).
- **Shift**: sin aplicarlo, la flag sale en minúsculas y el validador la rechaza.
- **Repeticiones**: dos informes iguales seguidos son la misma tecla mantenida; hay que decidir si cuenta una o dos.
- **Distribución**: el mapa HID es US; si el texto esperado no cuadra, revisar el mapeo (`-`, `_`, `{`, `}`).

- El tráfico USB sin cifrar expone lo que se escribe: teclados, mandos y lectores.
- Los informes HID son un formato fijo y sencillo; un script de 20 líneas basta.
- Un solo carácter mal mapeado invalida la flag: conviene validar la reconstrucción paso a paso.

## Mitigaciones y detección

No hay vulnerabilidad de software: el fallo es **físico**. Un sniffer USB ve todo lo que se teclea, incluida la flag.

- Cifrar o bloquear puertos USB en equipos sensibles y usar teclados con autenticación cuando el riesgo lo justifique.
- Detección: capturas USB con un dispositivo HID de apariencia desconocida y actividad de teclado sin sesión de usuario; en endpoint, drivers HID inyectados.
- Lección operativa: nunca teclear secretos en un equipo con un sniffer USB conectado.

## Referencias

- [pcap-triage](../../knowledge/forensics/pcap-triage.md)
## Método

1. **Aislar el dispositivo**: identificar la dirección del teclado y el endpoint de interrupción.

```bash
tshark -r usb.pcapng -Y 'usb.transfer_type == 0x01' -T fields -e usb.src -e usb.dst | sort | uniq -c
```

2. **Extraer los informes HID**: el byte 0 es el modificador (Shift) y el byte 2 el *keycode* de la tecla pulsada.

```bash
tshark -r deadly_arthropod.pcap -Y 'usb.transfer_type == 0x01 && frame.len == 35' \
  -T fields -e usb.capdata | grep -v '^0000000000000000$'
```

3. **Traducir**: con la tabla HID (USB HID Usage ID) cada keycode se convierte en carácter; los informes con `0000000000000000` son liberaciones (ignorar) y el modificador `02` o `20` indica Shift.

```python
# esqueleto: leer capdata, ignorar vacíos, mapear keycode -> char
```

4. **Leer el resultado**: la secuencia forma el texto tecleado con la flag. Conviene comprobar el orden y las mayúsculas carácter a carácter.
