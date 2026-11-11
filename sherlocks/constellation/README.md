---
sherlock: Constellation
domain: Threat Intelligence
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [threat-intelligence, pdf, metadata, exiftool, unfurl, insider]
---

# Constellation — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Una empleada recibe por Discord un documento con instrucciones para sacar datos de la empresa. El paquete de evidencias no trae disco ni captura: solo un PDF y una lista de IOCs. Hay que identificar al actor, la infraestructura y el momento en que se preparó el documento.

## Evidencias

```text
constellation/Artifacts/NDA_Instructions.pdf    documento enviado a la insider
constellation/Artifacts/IOCs.txt                URLs y dominios recopilados
```

```bash
sha256sum Artifacts/*        # anotar antes de abrir nada
exiftool Artifacts/NDA_Instructions.pdf
```

## Investigación

### 1. Inventario y triaje

Son dos ficheros pequeños, así que el orden lo marca el PDF: primero los metadatos, después el texto y por último las URLs de `IOCs.txt`. El PDF no lleva JavaScript ni adjuntos; el interés está en quién lo generó y con qué herramienta.

```bash
exiftool -a -G1 -s Artifacts/NDA_Instructions.pdf
```

### 2. Línea temporal

Los metadatos dan más de lo que parece: `Producer` y `Creator` apuntan a una herramienta propia del grupo, `Author` incluye un correo del actor y la fecha de creación es imposible (año 2054), señal de reloj manipulado o de una herramienta que escribe valores falsos. Las URLs de Discord y Google, descompuestas con Unfurl, aportan marcas de tiempo reales y el texto de la búsqueda que hizo la insider.

```bash
# pegar cada URL en https://dfir.blog/unfurl y leer timestamp y query
cat Artifacts/IOCs.txt
```

El orden reconstruido: reclutamiento por DM, entrega del PDF, búsqueda de instrucciones para empaquetar datos y subida a un bucket S3 con nombre provocador.

### 3. Artefacto clave

El PDF es el artefacto central: su texto describe exactamente qué comprimir y a dónde subirlo, y sus metadatos identifican al autor y la herramienta. La combinación de ambos convierte un documento genérico en prueba de preparación del delito.

## Conclusiones

- Actor: un grupo que se presenta como "AntiCorp" y recluta a un insider por Discord.
- Infraestructura: bucket S3 `hahaha-you-lose-forela`, CDN de Discord y búsquedas de Google usadas como canal encubierto.
- Técnica: instrucciones en PDF con metadatos descuidados y URLs con marcas de tiempo.
- IOC: autor y productor del PDF, dominio del bucket y las URLs de `IOCs.txt`.
- Qué falta: no hay evidencia de la exfiltración en sí, solo de la preparación.

## Lecciones

- Los metadatos de un documento son inteligencia: autor, herramienta y fechas imposibles sitúan al actor y su cadencia.
- Una URL de CDN o de búsqueda conserva identificadores y horas que el atacante no controla.
- El nombre del bucket también es un IOC reutilizable en otras campañas.
- Mitigación: formación sobre reclutamiento de insiders, DLP en el correo y en el chat corporativo, y bloqueo de dominios de almacenamiento no aprobados.
- Detección: documentos con `Producer` no corporativo, fechas futuras y usuarios que buscan cómo comprimir o subir datos.
- Lo que faltaría: retención de logs de proxy y de CASB para confirmar la subida.

MITRE: T1566 (phishing), T1583.001 (acquire infrastructure: domains), T1567.002 (exfiltration to cloud storage), T1078 (valid accounts).
