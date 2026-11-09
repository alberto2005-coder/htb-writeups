---
sherlock: Campfire-1
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, windows-events, kerberoasting]
---


# Campfire-1 — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Logs de un dominio Windows tras un incidente: la empresa sospecha que alguien está abusando de Kerberos. Se entregan eventos de seguridad y del controlador de dominio; hay que identificar al usuario comprometido, la técnica y desde qué equipo se trabajó.

## Evidencias

- `Security.evtx` y logs de servicio del DC.
- Export de eventos relacionados con Kerberos (4768, 4769, 4771).
- Inventario de equipos y cuentas de servicio.

## Investigación

### 1. Buscar el patrón de Kerberoasting

Un `4769` con **RC4 (0x17)** y un SPN de servicio para una cuenta sin relación con el usuario que lo pide es la firma:

```bash
EvtxECmd.exe -f Security.evtx --csv out/
grep "4769" out/*.csv | grep "0x17" | head -20
```

Se agrupa por cuenta solicitante y por `Service Name` para ver si es un pico puntual o una enumeración completa.

### 2. Del evento al host

Con el nombre de la cuenta y el `IpAddress` del evento se localiza la estación de trabajo. Se cruza con `4624` (tipo 3/10) y con el inicio de sesión interactivo previo, que suele ser el verdadero punto de entrada.

### 3. Qué se llevó

Los `4769` dicen qué servicios se pidieron; no dicen si el hash se crackeó. La comprobación está en el uso posterior de la cuenta: logins desde hosts nuevos, `4624` con tipo 3 hacia servidores de ficheros o correo.

## Conclusiones

- Actividad de Kerberoasting desde una estación concreta contra cuentas de servicio.
- El impacto depende de la fortaleza de las contraseñas de servicio, no del número de tickets.
- El punto de entrada es un usuario estándar comprometido, no el DC.

## Lecciones

- `4769` con RC4 y SPN es el evento que hay que saber leer de memoria.
- Rotar contraseñas de cuentas de servicio con 25+ caracteres o gMSA elimina la técnica.
- Sin telemetría de endpoint, el DC dice «qué» pero no «desde qué proceso».
