---
sherlock: Meerkat
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, suricata, credential-stuffing, cve-2022-25237, bonitasoft, persistence]
---

# Meerkat — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Forela usa una plataforma de gestión de procesos (**Bonitasoft BPM**) y sospecha que está comprometida. Se entregan un **PCAP** y el JSON de **alertas de Suricata** del periodo.

## Evidencias

```text
meerkat.pcap
meerkat-alerts.json
```

## Investigación

### 1. Alertas primero

```bash
jq -r '.alert.signature' meerkat-alerts.json | sort | uniq -c | sort -rn | headjq 'select(.alert.severity==1)' meerkat-alerts.json | head -40
```

Aparecen tres familias: intentos de login con el usuario por defecto (`ET WEB_SPECIFIC_APPS Bonitasoft Default User Login Attempt`), el bypass de autorización (`ET EXPLOIT Bonitasoft Authorization Bypass M1 (CVE-2022-25237)`) y tráfico de descarga hacia un paste externo.

### 2. Credential stuffing

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST" && http.request.uri contains "loginservice"' \
  -T fields -e frame.time -e ip.src -e http.user_agent | head -50
```

Cientos de `POST /bonita/loginservice` con `python-requests/2.28.1` y **pares usuario/contraseña distintos** desde la misma IP: es *credential stuffing*, no fuerza bruta sobre una cuenta. Termina en un `204`/`200` con cookies de sesión y una cuenta válida.

### 3. CVE-2022-25237

Bonita Web 2021.2 tiene un `RestAPIAuthorizationFilter` con un patrón de exclusión demasiado amplio: añadir **`;i18ntranslation`** (o `/../i18ntranslation/`) al final de la URL permite llamar a endpoints privilegiados sin permisos. En el PCAP se ve como peticiones a `/bonita/API/...` que devuelven `200` donde antes había `403`.

### 4. Extensión maliciosa y ejecución

```bash
tshark -r meerkat.pcap -Y 'http.request.method=="POST" && http.request.uri contains "pageUpload"' \
  -T fields -e frame.time -e ip.src -e http.request.uri
```

El actor sube un ZIP (`rce_api_extension.zip`) por `/bonita/API/pageUpload`, lo publica y llama a `/bonita/API/extension/rce?cmd=...`: ejecución de comandos como el usuario del servicio. Antes de usarlo comprueba con `whoami` y borra el ZIP para no dejar rastro.

### 5. Persistencia

El comando es un `wget` a **`pastes.io`**; el script descargado hace `curl` de una segunda paste y la **añade a `/home/ubuntu/.ssh/authorized_keys`**, luego reinicia `ssh`. Es la sub-técnica **T1098.004** (Account Manipulation: SSH Authorized Keys). Con la paste original borrada, la copia de Wayback Machine recupera el contenido.

## Conclusiones

- Acceso: credential stuffing contra `loginservice` con una cuenta corporativa válida.
- Escalada: CVE-2022-25237 para saltarse la autorización de la API.
- Ejecución: extensión subida por el propio panel (`pageUpload` → `extension/rce`).
- Persistencia: clave pública en `authorized_keys` del usuario `ubuntu`.

## Lecciones

- Las alertas dan el «qué»; el PCAP, el «cómo» y el «cuándo».
- Distinguir stuffing (usuarios variados) de spraying (misma contraseña) cambia la respuesta.
- Un endpoint que sube plugins es ejecución de código por diseño: hay que restringirlo.
- Mitigación: MFA y rate limiting en la API, parche de Bonita, allowlist de extensiones y monitorización de `authorized_keys`.
