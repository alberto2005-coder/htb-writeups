---
sherlock: Compromised
domain: DFIR / Red
difficulty: Easy
platform: Hack The Box
evidence: Captura de red de una red corporativa
tools: [Wireshark, tshark, NetworkMiner, VirusTotal]
state: Retired
tags: [dfir, network-forensics, pcap, malware-triage, dns-tunneling]
---

# Compromised — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

El SOC detecta actividad sospechosa en el tráfico: un equipo de la red corporativa está comprometido y se han llevado información que no debía salir. Se entrega un único PCAP; hay que reconstruir el acceso inicial, clasificar el malware y decir qué se exfiltró.

## Evidencias

- `capture.pcap`.

## Investigación

1. **Panorama**: quién habla con quién y cuánto.

```bash
tshark -r capture.pcap -q -z conv,ip
```

2. **Descarga inicial**: el host víctima pide por HTTP en claro un fichero con nombre de imagen (`6ctf5JL.gif`) a `162.252.172.54`, pero el contenido es un **DLL PE**.

```bash
tshark -r capture.pcap -Y 'http.request' -T fields -e ip.dst -e http.host -e http.request.uri
```

`Export Objects` trunca el flujo: hay que reensamblar el TCP, comprobar con `file` que es un PE y **entonces** calcular el SHA-256, o el hash no cuadra con el de ninguna base de datos.

3. **Clasificación**: ese SHA-256 en VirusTotal lo identifica como **Pikabot** (loader); de la misma ficha salen la familia y la fecha de primera observación, que es lo que piden las preguntas de atribución.

4. **C2**: tras la ejecución el host habla **HTTPS con certificados autofirmados** contra hosts externos en puertos no estándar (2078, 2222 y 3299).

```bash
tshark -r capture.pcap -Y 'ssl.handshake.type==11' -T fields -e ip.dst -e tcp.port -e x509sat.printableString
```

5. **Exfiltración**: el canal final no es HTTP ni TLS sino **DNS**: nombres largos y volumen anómalo hacia un dominio del atacante, patrón de túnel.

```bash
tshark -r capture.pcap -Y dns -T fields -e dns.qry.name | sort | uniq -c | sort -rn | head
```

## Conclusiones

Un solo PCAP contiene la cadena completa: DLL de Pikabot descargado por HTTP desde `162.252.172.54`, balizas TLS autofirmadas en puertos altos y salida por túnel DNS. La familia se atribuye con VirusTotal, no descifrando el tráfico.

## Lecciones

- La descarga se disfraza de imagen: el nombre no dice nada, la firma `MZ` sí.
- El export de objetos de Wireshark trunca flujos grandes; reensamblar antes de hashear.
- Tres protocolos distintos (HTTP, TLS, DNS) y solo la visibilidad de red los une.

## Qué enseña

- Un C2 moderno cambia de canal en cada fase: descarga, balizas y salida.
- Los certificados autofirmados en puertos altos son una señal barata y potente.
- El túnel DNS se detecta por volumen y longitud de nombre, sin descifrar nada.

## Tropiezos

- **TLS**: sin claves no se lee el contenido; el análisis va por metadatos (SNI, certificado, puertos, volúmenes).
- **Ruido**: separar el descubrimiento del tráfico de explotación.
- **Hashes**: hashear el objeto exportado en vez del flujo reensamblado da un valor que no existe en ninguna base.
