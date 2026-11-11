---
sherlock: Trent
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, router, firmware, command-injection, cve-2024-28353]
---

# Trent — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

El SOC detecta movimiento lateral contra el router de una sede. La única evidencia es una captura de unos 17 minutos tomada en el interior de la red. Hay que identificar al host atacante, la vulnerabilidad del firmware y qué se ejecutó después.

## Evidencias

```text
trent/trent.pcap        captura Linux cooked-mode, ~81.000 paquetes
```

```bash
capinfos trent.pcap
tshark -r trent.pcap -q -z endpoints,ip
```

## Investigación

### 1. Inventario y triaje

`capinfos` da duración y número de paquetes; `endpoints` revela tres o cuatro hosts. El router es la puerta de enlace y el host interno que más peticiones HTTP genera es el sospechoso. Se filtran las peticiones HTTP hacia el panel de administración.

```bash
tshark -r trent.pcap -Y 'http.request && ip.dst==192.168.10.1' -T fields -e frame.time -e ip.src -e http.request.method -e http.request.uri | head
```

### 2. Línea temporal

Primero un login en el panel web del router, después una petición `POST /apply.cgi` con el parámetro `usbapps.config.smb_admin_name` cargado con metacaracteres. La respuesta confirma la ejecución. Poco después el router descarga un script y abre una conexión saliente al C2.

### 3. Artefacto clave

La inyección de comandos en `apply.cgi` es **CVE-2024-28353** en el firmware del TRENDnet TEW-827DRU: el campo `smb_admin_name` se pasa a una shell sin sanear. Siguiendo el flujo TCP de la descarga se lee el script, que lanza una reverse shell a `35.159.25.253:41143`. La versión del firmware aparece en las respuestas HTTP y permite confirmar la CVE.

```bash
tshark -r trent.pcap -Y 'http.request.method=="POST" && http.request.uri contains "apply.cgi"' -T fields -e http.file_data | head -c 600
```

## Conclusiones

- Entrada: credenciales del panel del router y una inyección de comandos autenticada en `apply.cgi`.
- Vulnerabilidad: CVE-2024-28353, falta de saneo de `usbapps.config.smb_admin_name`.
- Acción: descarga de un script y reverse shell al C2 `35.159.25.253:41143`.
- IOC: IP y puerto del C2, ruta del script y el parámetro usado en el POST.
- Persistencia: no visible en la captura; el router no se reinicia en la ventana.

## Lecciones

- Los paneles de administración de dispositivos de red son superficie interna: un login exitoso seguido de `apply.cgi` merece revisión.
- La captura interna basta para identificar la CVE si se registra la versión del firmware en las respuestas.
- Un router comprometido da salida a internet sin pasar por el proxy: la conexión saliente es el IOC más útil.
- Mitigación: actualizar el firmware, cambiar credenciales por defecto y segmentar la gestión de red en una VLAN aislada.
- Detección: POST a `apply.cgi` con metacaracteres, descargas de scripts desde el router y conexiones salientes desde equipos de red.
- Lo que faltaría: syslog del router y NetFlow para confirmar el volumen enviado.

MITRE: T1190 (exploit public-facing application), T1059.004 (Unix shell), T1105 (ingress tool transfer), T1071.001 (web protocols).
