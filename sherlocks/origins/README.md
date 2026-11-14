---
sherlock: Origins
category: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, ftp, brute-force, s3, data-exfiltration]
---

# Origins — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una empresa detecta accesos anómalos a su servidor FTP. Se entrega una captura de red y se pide identificar el origen del ataque, las credenciales comprometidas, los archivos sustraídos y el impacto posterior.

## Evidencias

- `capture.pcap` con tráfico FTP y otras conexiones.
- No se entrega imagen de disco ni logs del servidor.
- La captura contiene las credenciales y las transferencias.

```bash
capinfos capture.pcap
tshark -r capture.pcap -Y ftp -T fields -e ip.src -e ip.dst -e ftp.request.command -e ftp.request.arg
```

## Investigación

### 1. Inventario y triaje

Se revisan conversaciones y protocolos. Un host externo envía un volumen alto de intentos de login FTP en pocos segundos; el patrón es fuerza bruta, no navegación normal.

- IP atacante: `<ATTACKER_IP>`.
- Servicio: FTP en el puerto 21.
- Ventana temporal: `<START>` a `<END>`.
- User-Agent/versión del servidor: visible en el banner.

### 2. Credenciales y acceso

Se filtran las respuestas `230 Login successful`. El primer login válido marca el fin de la fuerza bruta. Al seguir el stream se ven el usuario y la contraseña usados.

```bash
tshark -r capture.pcap -Y 'ftp.response.code == 230' -T fields -e frame.time -e ip.src -e ftp.request.arg
```

La contraseña se redacta; se anota solo el nombre de usuario.

### 3. Exfiltración

Tras el login, el atacante lista directorios y descarga archivos con `RETR`. Los objetos FTP-DATA se extraen desde Wireshark (`File → Export Objects → FTP-DATA`).

```bash
tshark -r capture.pcap -Y 'ftp.request.command == "RETR"' -T fields -e ftp.request.arg
```

Los archivos contienen:

- `s3_buckets.txt` con enlaces a buckets de 2022 y 2023.
- `Maintenance-Notice.pdf` con una contraseña de servidores de backup.
- Una dirección de correo de contacto para solicitar acceso.

## Conclusiones

- El acceso inicial fue fuerza bruta contra FTP.
- Se descargaron inventarios y documentación interna.
- Los buckets S3 quedaron expuestos y uno contenía datos históricos.
- El correo de contacto es un objetivo probable de phishing.

## Lecciones

- FTP sin límites de intentos permite fuerza bruta.
- Los archivos de mantenimiento no deben contener contraseñas.
- Un bucket S3 mal configurado amplifica el impacto de una credencial FTP.

## Referencias

- <https://www.hackthebox.com/sherlocks/Origins>
- <https://attack.mitre.org/techniques/T1110/001/>
- <https://attack.mitre.org/techniques/T1048/>
- <https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html>
