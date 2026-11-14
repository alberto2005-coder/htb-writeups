---
topic: Envenenamiento ARP y DNS
tags: [forensics, arp, dns, spoofing, pcap, mitm, layer2]
---

# Envenenamiento ARP y DNS

[🌐 English](arp-dns-poisoning.en.md) | **Español**

## Concept

ARP no tiene autenticación: un host puede anunciar que la IP del gateway corresponde a su MAC. Si lo consigue, el tráfico pasa por el atacante. Con DNS falso, las víctimas resuelven dominios legítimos hacia servidores controlados y descargan malware o entregan credenciales.

## Cuándo aplica

- Redes Wi-Fi compartidas o VLAN sin inspección.
- Capturas con respuestas ARP duplicadas.
- DNS que apunta a una IP inesperada.
- Descargas HTTP de actualizaciones o instaladores.
- Tráfico de un host que no es el gateway.

## Procedimiento

1. Contar ARP requests y replies por MAC/IP.
2. Identificar MAC duplicadas para la IP del gateway.
3. Revisar consultas y respuestas DNS.
4. Comparar la IP resuelta con la legítima.
5. Extraer el archivo descargado y analizarlo.

```bash
tshark -r capture.pcap -Y arp -T fields -e arp.opcode -e arp.src.proto_ipv4 -e arp.src.hw_mac | sort | uniq -c
tshark -r capture.pcap -Y 'dns.flags.response == 1' -T fields -e dns.qry.name -e dns.a
```

## Variantes

- ARP spoofing del gateway y de la víctima.
- DNS spoofing con respuestas falsas.
- DHCP rogue para asignar un gateway malicioso.
- Proxy transparente para interceptar HTTP.
- SSL stripping cuando el sitio no fuerza HTTPS.

## Limitaciones

- La red debe permitir ARP broadcast.
- Dynamic ARP Inspection o port security lo bloquean.
- HSTS y certificados válidos limitan el impacto.
- El atacante debe estar en el mismo segmento.

## Mitigación y detección

- Habilitar Dynamic ARP Inspection y DHCP snooping.
- Usar DNSSEC, DNS over HTTPS y resolver controlado.
- Segmentar la red y evitar Wi-Fi abiertas para trabajo.
- Alertar de MAC duplicadas, cambios de gateway y dominios recién registrados.

## Referencias

- <https://attack.mitre.org/techniques/T1557/002/>
- <https://attack.mitre.org/techniques/T1557/001/>
- <https://www.rfc-editor.org/rfc/rfc826.html>
- <https://www.wireshark.org/docs/wsug_html_chunked/>
