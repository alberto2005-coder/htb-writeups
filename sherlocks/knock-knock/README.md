---
sherlock: Knock Knock
domain: Network Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, pcap, password-spray, ftp, port-knocking, ssh, ransomware, osint]
---

# Knock Knock — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Un servidor de desarrollo de Forela quedó expuesto a internet por error. El equipo cree que estaba endurecido y no entiende cómo entraron. Hay una captura de red de uno o dos días alrededor del incidente; el objetivo es reconstruir el acceso y lo que se hizo después.

## Evidencias

```text
capture.pcap
```

## Investigación

### 1. Barrido y objetivo

```bash
tshark -r capture.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src -e ip.dst -e tcp.dstport | sort | uniq -c | sort -rn | head
```

Una IP externa prueba decenas de puertos contra una interna: es un escaneo. El host con más puertos probados es el servidor de desarrollo.

```bash
capinfos capture.pcap
tshark -r capture.pcap -q -z conv,tcp | head
```

### 2. Fuerza bruta contra FTP

```bash
tshark -r capture.pcap -Y 'ftp' -T fields -e ip.src -e ip.dst -e ftp.request.command -e ftp.request.arg | head -40
```

Se ven muchos `USER`/`PASS` fallidos seguidos de un `230 Login successful`: **password spray** contra el servicio expuesto. A partir de ahí, `LIST`, `RETR` de ficheros de configuración.

### 3. Del FTP al servicio oculto

Entre los ficheros descargados hay configuración de **port knocking** (reglas de `knockd`). La secuencia de golpes abre un puerto que el escaneo no vio:

```bash
tshark -r capture.pcap -Y 'tcp.dstport==<puerto1> || tcp.dstport==<puerto2> || tcp.dstport==<puerto3>' -T fields -e frame.time -e ip.src -e tcp.dstport
```

Tras la secuencia aparece un `SYN` con `SYN/ACK` en el puerto crítico (SSH), que antes estaba filtrado.

### 4. Acceso, jail y ransomware

- Credenciales válidas en el servicio recién abierto: `230`/login correcto y sesión establecida.
- **Escape de chroot**: con traversal (`../../`) el atacante sale del directorio jaulado y llega al sistema real.
- Descarga de la carga final con `wget` y ejecución: ransomware tipo **GonnaCry**, cifrado de ficheros del servidor.

La parte de OSINT del reto se resuelve buscando en fuentes públicas los datos de la empresa que aparecen en la captura (correos, nombres, calendario).

## Conclusiones

- Entrada: password spray contra un FTP expuesto a internet.
- Movimiento: configuración de port knocking leída desde el FTP; la secuencia abre SSH.
- Impacto: escape de chroot y despliegue de ransomware.

## Lecciones

- La seguridad por ocultación (puerto cerrado) cae si la configuración está en un FTP mal protegido.
- Un chroot no es un sandbox: sin privilegios correctos se escapa con traversal.
- Mitigación: nada de servicios de desarrollo en internet, MFA, contraseñas robustas y copias de seguridad inmutables.
