---
machine: Explosion
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [windows, rdp, blank-password, misconfiguration]
---

# Explosion — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available (Starting Point), publicable.
> Ficha de referencia. Sin flags ni credenciales reales.

## TL;DR

Un Windows con **RDP abierto y la cuenta `Administrator` sin contraseña**. No hay exploit: se conecta uno por escritorio remoto, se acepta el certificado y se entra con el campo de contraseña vacío. La flag está en el escritorio del administrador.

## Reconocimiento

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
135/tcp   msrpc        Microsoft Windows RPC
139/tcp   netbios-ssn
445/tcp   microsoft-ds
3389/tcp  ms-wbt-server  Microsoft Terminal Services
```

Tres puertos de SMB/RPC y el 3389 de escritorio remoto. Con SMB se puede listar sin credenciales, pero no hace falta: el 3389 es la puerta.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
xfreerdp /v:<IP> /cert:ignore /u:Administrator
```

En la ventana de credenciales se pulsa **Enter sin escribir nada**: la cuenta no tiene contraseña y la política permite el acceso.

```bash
# alternativa
rdesktop <IP> -u Administrator -p ""
```

Ya en el escritorio:

```text
C:\Users\Administrator\Desktop\flag.txt
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

```text
C:\Users\Administrator\Desktop\flag.txt  -> <flag>
```

## Lecciones aprendidas

- Una cuenta con contraseña vacía y RDP expuesto es acceso total sin exploit; la política de Windows lo permite por defecto en equipos que no están en dominio.
- Mitigación: `LimitBlankPasswordUse = 1`, exigir NLA (`UserAuthentication = 1`), cuentas locales con contraseña y RDP solo por VPN o detrás de un jump host.
- Detección: eventos 4624 tipo 10 desde direcciones no habituales y 4625 repetidos con usuario `Administrator`.

## Mitigaciones y detección

- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- Documentación de la plataforma y del servicio afectado.
