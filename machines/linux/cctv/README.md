---
machine: CCTV
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, zoneminder, sqli, tcpdump, motioneye]
---

# CCTV — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

ZoneMinder 1.37.63 conserva credenciales por defecto y es vulnerable a CVE-2024-51482, una SQLi ciega en el manejo de eventos. Se vuelca la base, se crackea el hash bcrypt de `mark` y se entra por SSH. `mark` puede capturar tráfico y ve la contraseña de `sa_mark` en claro; con ella se accede a motionEye en localhost y se explota CVE-2025-60787 para ejecutar comandos como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 24.04 y `80/tcp` Apache con `cctv.htb`.
- `/zm/` sirve ZoneMinder 1.37.63 y acepta `admin:admin`.
- No hay subdominios adicionales; el resto de la aplicación es estático.

## Enumeración

- La versión 1.37.63 está afectada por CVE-2024-51482, una SQLi ciega en `AddMonitorsTable`.
- `sqlmap` confirma la inyección temporal y enumera usuarios y hashes bcrypt.
- El hash de `mark` se crackea con `hashcat -m 3200`.

## Foothold

Se usa `sqlmap` con la cookie de sesión para volcar la base y se entra por SSH como `mark`.

```bash
sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=...' --cookie='ZMSESSID=<SESSION>' --batch --dump
hashcat -m 3200 zm.hashes rockyou.txt
ssh mark@cctv.htb
```

## Movimiento lateral

`mark` está en el grupo de `tcpdump`, así que captura el tráfico del puerto `5000`. El protocolo de gestión de las cámaras envía la contraseña de `sa_mark` en claro; esa contraseña se reutiliza para `su`.

## Escalada de privilegios

motionEye escucha en `localhost:8765`. Se crea un túnel SSH, se entra con el usuario `admin` y la contraseña de `sa_mark`, y se explota CVE-2025-60787 en el nombre de la imagen para ejecutar comandos como root.

```bash
ssh -L 8765:localhost:8765 mark@cctv.htb
# En motionEye: Settings -> Still Images -> filename
# Payload de CVE-2025-60787
```

## Evidencia

- ZoneMinder con credenciales por defecto y SQLi confirmada.
- Hash de `mark` crackeado y captura de `tcpdump`.
- Acceso a motionEye y ejecución como root.

## Lecciones aprendidas

- Las credenciales por defecto siguen apareciendo en productos de video vigilancia.
- Una SQLi ciega basta para volcar hashes si la sesión es válida.
- El tráfico de gestión sin cifrar expone contraseñas reutilizables.

## Mitigación y detección

- Actualizar ZoneMinder y motionEye; cambiar credenciales por defecto.
- Cifrar el protocolo de gestión y segmentar las cámaras.
- Restringir `tcpdump` y revisar capturas no autorizadas.

## Referencias

- [0xdf — CCTV](https://0xdf.gitlab.io/2026/07/11/htb-cctv.html)
- [IppSec — CCTV](https://www.youtube.com/watch?v=C60J33Mbd5E)
- [Hack The Box — CCTV](https://app.hackthebox.com/machines/cctv)
