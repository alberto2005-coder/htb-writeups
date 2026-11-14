---
topic: Data exfiltration
tags: [general, exfiltration, dns, http, smb, dlp]
---

# Data exfiltration

[🌐 English](data-exfiltration.en.md) | **Español**

## Concepto

La exfiltración extrae datos del entorno comprometido por canales permitidos: HTTP/S, DNS, SMB, correo o almacenamiento cloud. El análisis busca volumen, destino, codificación y horario anómalos, no solo una conexión sospechosa.

## Cuándo aplica

- Transferencias grandes hacia un host externo.
- Consultas DNS con cadenas codificadas.
- Uso de un webhook, pastebin o bucket.
- Movimiento de datos antes del cifrado o borrado.

## Procedimiento

1. Identificar datos sensibles y su ubicación.
2. Revisar conexiones salientes y volúmenes.
3. Analizar DNS, HTTP y SMB en busca de codificación.
4. Correlacionar con procesos y cuentas.
5. Documentar destino, tamaño y periodo.

```bash
tcpdump -r capture.pcap -nn 'port 53 or port 80 or port 443'
tshark -r capture.pcap -Y 'dns.qry.name contains "<DOMAIN>"'
```

## Variantes

- DNS tunneling con subdominios codificados.
- HTTP POST a un webhook.
- Copia a un bucket S3 o a un recurso compartido.
- Exfiltración por correo o mensajería.

## Limitaciones

- El tráfico puede estar cifrado.
- El volumen puede dividirse en transferencias pequeñas.
- Los destinos legítimos pueden ocultar la actividad.
- Sin telemetría de endpoint, el origen es difícil de atribuir.

## Mitigación y detección

- Aplicar DLP y restringir destinos.
- Monitorizar volúmenes, DNS y conexiones nuevas.
- Bloquear webhooks y almacenamiento no aprobados.
- Alertar de compresión y cifrado masivo antes de una salida.

## Referencias

- <https://attack.mitre.org/techniques/T1041/>
- <https://attack.mitre.org/techniques/T1048/003/>
- <https://www.cisa.gov/resources-tools/resources/data-loss-prevention>
