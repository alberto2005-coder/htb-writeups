---
sherlock: Meerkat
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, suricata, credential-stuffing, cve-2022-25237, persistence]
---


# Meerkat — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Forela usa una plataforma de gestión de procesos (Bonitasoft BPM) y sospecha que está comprometida. Se entrega un **PCAP** y el JSON de **alertas de Suricata** del periodo del incidente. Hay que confirmar si hubo intrusión y reconstruirla.

## Evidencias

```text
meerkat.pcap
meerkat-alerts.json
```

## Investigación

### 1. Alertas primero, paquete después

```bash
jq -r '.alert.signature' meerkat-alerts.json | sort | uniq -c | sort -rn
jq 'select(.alert.severity==1)' meerkat-alerts.json | head -40
```

La alerta dominante suele apuntar al vector: intentos masivos contra el login de la API. Se anotan IP origen, `timestamp` y `flow_id`, y se localiza esa conversación en el PCAP con Wireshark (`ip.addr==... && tcp.port==...`).

### 2. Fuerza bruta / credential stuffing

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST"' \
  -T fields -e frame.time -e ip.src -e http.request.uri -e http.user_agent | head -50
```

Cientos de `POST /bonita/loginservice` con distintos usuarios y códigos `401`/`403`, seguidos de un `200` y una cookie de sesión: ahí está el punto de inflexión. Se identifica la cuenta válida y el instante exacto.

### 3. Bypass de autorización y extensión maliciosa

Tras autenticarse, el actor abusa de **CVE-2022-25237**: un fallo en la validación del parámetro `options` de la API permite saltarse los controles de autorización y llegar a funciones de administración. Se ve en el PCAP como peticiones a `/bonita/API/...` con parámetros manipulados que devuelven `200` donde antes había `403`.

Con privilegios, sube una **extensión/página** propia (un `.zip` con código) que el servidor despliega y ejecuta:

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST" && http.content_type contains "multipart"' \
  -T fields -e frame.time -e ip.src -e http.request.uri -e http.file_data | head
```

## Conclusiones

- Acceso: credential stuffing contra `loginservice` con una cuenta válida.
- Escalada: CVE-2022-25237 para saltarse la autorización de la API.
- Ejecución: extensión maliciosa subida por el propio panel de administración.

## Lecciones

- Las alertas de Suricata dan el «qué»; el PCAP da el «cómo» y el «cuándo». Sin cruzar ambos, la cronología se queda en hipótesis.
- Credential stuffing se detecta por volumen y por variedad de usuarios desde una misma IP, no por un payload concreto.
- Mitigación: rate limiting, MFA en la API, parchear CVE-2022-25237 y restringir quién puede subir extensiones.
