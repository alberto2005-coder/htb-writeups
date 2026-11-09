---
title: Triaje de PCAP — de la captura a la evidencia
tags: [forensics, pcap, wireshark, tshark, dfir]
---

# Triaje de PCAP

[🇬🇧 English](pcap-triage.en.md) | **Español**

## 1. Inventario antes de abrir

```bash
capinfos capture.pcapng
tshark -r capture.pcapng -q -z io,phs
```

`io,phs` da la jerarquía de protocolos: si aparece HTTP, DNS, SMB o TLS, ya sabes dónde mirar. Después, conversaciones y endpoints:

```bash
tshark -r capture.pcapng -q -z conv,tcp
tshark -r capture.pcapng -q -z endpoints,ip
```

## 2. HTTP en claro

```bash
tshark -r capture.pcapng --export-objects http,out/
tshark -r capture.pcapng -Y 'http.request' -T fields -e http.host -e http.request.uri | sort -u
tshark -r capture.pcapng -Y 'http.request.method=="POST"' -T fields -e http.file_data | head
```

Credenciales y flags suelen estar en `POST` con `application/x-www-form-urlencoded` o en básica (`Authorization: Basic`). Para seguir una conversación:

```bash
tshark -r capture.pcapng -q -z follow,tcp,ascii,<stream>
```

## 3. DNS y exfiltración

```bash
tshark -r capture.pcapng -Y dns -T fields -e dns.qry.name | sort -u | head -50
```

Si los subdominios son largos y aleatorios, es túnel DNS: concatena las etiquetas, decodifica base32/base64url y ordena por tiempo (`-e frame.time`). `dnscat2` y `iodine` tienen firmas reconocibles en la longitud y el alfabeto.

## 4. Otros protocolos que dan puntos

- **SMB/NTLM**: `-Y ntlmssp` muestra el `NTLMSSP_AUTH` con usuario y dominio; con `-Y smb2` ves ficheros y rutas.
- **FTP**: `-Y ftp` deja usuario, contraseña y `RETR`.
- **USB HID**: `-Y 'usb.capdata'` con el mapa de teclas; reconstruye pulsaciones (`usbhid-dump` no sirve sobre un pcap).
- **TLS**: sin clave no hay contenido; busca `ClientHello` con SNI y certificados en claro.
- **ICMP/DNS tunneling**: tamaños anómalos y muchos paquetes al mismo destino.

## 5. Correlacionar y responder

1. Fija la **ventana temporal** del incidente (`frame.time`).
2. Identifica **quién habló con quién** (conversaciones, endpoints).
3. Extrae el **artefacto** (fichero, credencial, comando) y guárdalo con hash.
4. Cruza con logs del host (Sysmon, auth.log) para confirmar ejecución.

```bash
sha256sum out/*
```

## 6. Errores típicos

- **`tshark` no ve HTTP** → el tráfico va por 8080/8443 o TLS: ajusta filtros y puertos.
- **`--export-objects` extrae basura** → el flujo está comprimido (`Content-Encoding: gzip`); descomprime el objeto.
- **Muchos nombres DNS y ninguno útil** → ordena por longitud y por tiempo, no alfabéticamente.
- **Falta el handshake** → la captura empieza a mitad; no podrás descifrar TLS.
- **`capinfos` falla** → el fichero está truncado; prueba `editcap -F pcap` o `tcpdump -r`.

## 7. Detección y mitigación

- Retención de PCAP en el perímetro y en endpoints críticos; sincronización de relojes.
- Alertas de túneles DNS (longitud de etiqueta, volumen, entropía) y de HTTP en claro con credenciales.
- Segmentación para que el tráfico interno no sea visible desde un solo punto.
- En DFIR, documenta filtros y comandos exactos: la reproducibilidad es la evidencia.

MITRE: T1048, T1071.004, T1040.
