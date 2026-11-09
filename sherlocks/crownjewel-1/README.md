---
sherlock: CrownJewel-1
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, dcsync, golden-ticket, domain-admin]
---


# CrownJewel-1 — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un dominio Windows aparece con actividad administrativa que nadie reconoce. Se entrega telemetría de los controladores y de un par de servidores; el objetivo es determinar cómo se obtuvo el control del dominio y qué cuentas quedaron comprometidas.

## Evidencias

- Logs de seguridad de DC y servidores miembros.
- Eventos de replicación de directorio (4662) y de acceso a servicios.
- Artefactos de endpoint de los hosts implicados.

## Investigación

### 1. Replicación no autorizada

`4662` con el GUID de replicación (`1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`) y una cuenta que no es de máquina apunta a **DCSync**:

```bash
grep "4662" Security.evtx | grep -i "1131f6aa" | head
```

Se identifica la cuenta que pidió la replicación y el host desde el que se hizo.

### 2. Fase previa

DCSync no es el primer paso. Se busca el otorgamiento de derechos (`DS-Replication-Get-Changes`) en los logs de cambios de ACL, y el compromiso de la cuenta que los tenía: phishing, contraseña reutilizada o un servicio expuesto.

### 3. Persistencia

```bash
grep "4769" Security.evtx | grep -i "krbtgt" | head
```

Tickets para `krbtgt` desde hosts no-DC sugieren **golden ticket**. El `4768` sin `4624` previo y con `Ticket Options` atípicas refuerza la hipótesis.

## Conclusiones

- Escalada hasta control de dominio mediante replicación de directorio con una cuenta comprometida.
- Persistencia probable con ticket dorado: rotar `krbtgt` dos veces es obligatorio.

## Lecciones

- `4662` + GUID de replicación es la evidencia más limpia de DCSync.
- Un golden ticket no deja `4624`: por eso hay que mirar `4768`/`4769` en el DC.
- La respuesta a un compromiso de dominio empieza por `krbtgt`, no por el endpoint.
