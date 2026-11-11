---
sherlock: MisCloud
domain: Cloud
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [cloud, gcp, gitea, pcap, audit-logs, service-account]
---

# MisCloud — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Una empresa migra de WordPress a Google Cloud con un Gitea autohospedado. Días después, datos de clientes aparecen cifrados y fuera de la organización. El paquete trae la captura de red de la VPC y los logs de auditoría de GCP; hay que reconstruir el acceso, el pivote y la exfiltración.

## Evidencias

```text
miscloud/VPCNetwork_Traffic.pcap        tráfico interno de la VPC
miscloud/GCloud_Logs.json               audit logs de Cloud Audit
miscloud/inventory.json                 inventario de VMs y buckets
```

```bash
sha256sum *                             # anotar antes de analizar
jq '.[0]' GCloud_Logs.json | head -40
```

## Investigación

### 1. Inventario y triaje

La captura se abre primero con estadísticas de conversaciones para localizar el host que más habla y los servicios internos. En paralelo, `jq` sobre los audit logs lista los métodos invocados y las identidades que los llaman.

```bash
tshark -r VPCNetwork_Traffic.pcap -q -z conv,tcp | head -20
jq -r '.[].protoPayload.methodName' GCloud_Logs.json | sort | uniq -c | sort -rn | head
```

### 2. Línea temporal

El pico coincide con peticiones HTTP POST a `/git/post-receive` en el Gitea interno: un hook del repositorio ejecuta el contenido que llega. Desde ahí el atacante descarga y ejecuta un script en bash pasado por base64, y empieza a usar la cuenta de servicio `compute@developer.gserviceaccount.com` para leer el bucket de datos.

El orden: acceso al panel de Gitea, creación o abuso del hook, ejecución de comandos, creación de un fichero cifrado y subida por HTTP.

### 3. Artefacto clave

El hook `post-receive` es la pieza que convierte un repositorio en ejecución remota. En los logs de auditoría, las llamadas de la cuenta de servicio a `storage.objects.get` desde una IP que no es de la VM documentada prueban el pivote. La captura conserva el POST con el script y la respuesta con el fichero cifrado.

```bash
jq -r '.[] | select(.protoPayload.authenticationInfo.principalEmail|test("compute@developer")) | [.timestamp, .protoPayload.methodName] | @tsv' GCloud_Logs.json | head
```

## Conclusiones

- Entrada: abuso de un Gitea expuesto y de su hook `post-receive` para ejecutar comandos.
- Pivote: la cuenta de servicio por defecto de Compute Engine, con permisos sobre Cloud Storage.
- Exfiltración: datos de clientes cifrados con un script propio y subidos por HTTP.
- IOC: ruta del hook, user-agent y IP del atacante, y el identificador de la cuenta de servicio usada fuera de la VM.
- Persistencia: el propio hook del repositorio.

## Lecciones

- Un Gitea accesible desde internet con hooks habilitados es ejecución de código, no solo un repositorio.
- La cuenta de servicio por defecto suele tener más permisos de los necesarios; su uso desde otra IP es una señal fuerte.
- Los audit logs de GCP dan identidad y método; la captura da el contenido. Ninguno basta solo.
- Mitigación: quitar la cuenta de servicio por defecto de las VMs, aplicar mínimo privilegio en buckets y restringir Gitea por VPN.
- Detección: `storage.objects.get` masivo, llamadas de servicio desde IPs externas y peticiones a `post-receive` con cuerpos largos.
- Lo que faltaría: logs del balanceador para ver el escaneo previo y el origen real.

MITRE: T1190 (exploit public-facing application), T1059.004 (Unix shell), T1078.004 (cloud accounts), T1530 (data from cloud storage), T1567.002 (exfiltration to cloud storage).
