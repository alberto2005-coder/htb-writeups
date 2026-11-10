---
sherlock: Nubilum-1
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
state: Retired
evidence: CloudTrail, artefactos de una EC2 (CatScale), copia de S3 y entrevista
tools: [jq, AWS CLI, Splunk, CyberChef]
tags: [dfir, cloud, aws, cloudtrail, ec2, s3, poshc2]
---

# Nubilum-1 — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Amazon avisa de que una **EC2** de la cuenta se está usando con fines maliciosos. El administrador de nube no recuerda haberla desplegado, pero sí recuerda haber visto **más de seis instancias** corriendo al entrar en la consola. Se entrega la entrevista de triaje, los logs de **CloudTrail**, una captura de la instancia con **CatScale**, una copia del bucket y un directorio «raro».

## Evidencias

```text
CloudTrail/949622803460/CloudTrail/<región>/*.json   (~8.700 ficheros)
catscale_ip-172-31-24-20-20230130-1628.tar.gz        (artefactos de la EC2)
forela-storage/                                      (copia del bucket S3)
unusual-directory.zip                                 (directorio hallado en el host)
interview.txt                                         (entrevista al sysadmin)
```

## Investigación

### 1. Normalizar CloudTrail

Los JSON vienen en `Records[]` y troceados por región; primero se fusionan y se ordenan por tiempo, o no hay cronología posible.

```bash
jq -s '[.[].Records[]] | sort_by(.eventTime)' CloudTrail/*/*.json > merged.json
jq -r '.[] | [.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress] | @tsv' merged.json | sort > timeline.tsv
```

### 2. La identidad comprometida

La entrevista dice qué usuarios y roles existen; lo que **no** salga de ahí es del atacante. El patrón habitual: un usuario de automatización de EC2 con permisos de creación de instancias y de claves.

```bash
jq -r '.[].userIdentity.arn' merged.json | sort | uniq -c | sort -rn | head
jq -r '.[] | select(.eventName|test("RunInstances|CreateKeyPair|CreateAccessKey")) | [.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress] | @tsv' merged.json
```

### 3. Dónde estaban las claves

En la copia del bucket hay un script de respaldo con un par `access_key`/`secret_key` en claro. Buscar el prefijo `AKIA` localiza el fichero y su ruta dentro del bucket.

```bash
grep -rn "AKIA" forela-storage/ | head
```

### 4. Línea temporal del abuso

Con el usuario identificado se aíslan sus `sourceIPAddress`: varias direcciones del mismo rango, en orden ascendente, separadas de las del tráfico legítimo. De ahí salen las horas de creación de instancias y de pares de claves.

```bash
jq -r '.[] | select(.userIdentity.arn|test("<usuario-automatizacion>")) | .sourceIPAddress' merged.json | sort -u
```

### 5. El implante

`unusual-directory.zip` contiene el framework de C2 instalado en la instancia: **PoshC2**. En el `tar.gz` de CatScale se confirma con la lista de procesos, los puertos en escucha y los ficheros del directorio de instalación.

```bash
tar xzf catscale_*.tar.gz && ls -R | head -40
grep -rl "poshc2\|PoshC2" . | head
```

## Conclusiones

- Entrada: claves IAM de un usuario de automatización **hardcodeadas** en un script dentro de un bucket S3.
- Abuso: creación de pares de claves e instancias EC2 adicionales desde IPs del atacante.
- Implantación: **PoshC2** en la instancia denunciada por AWS.
- Persistencia probable: claves y usuarios creados que sobreviven al borrado de la instancia.

## Lecciones

- CloudTrail es el PCAP de la nube: identidad, acción, hora y origen en cada evento.
- Casi 9.000 ficheros se resuelven con `jq`, no abriéndolos: fusionar, deduplicar por `eventID` y filtrar por `eventName`.
- La entrevista define la **línea base**: sin ella no se distingue lo legítimo de lo añadido.
- Borrar la instancia no revoca las claves creadas antes: hay que rotar y auditar IAM.
- Un secreto en un script de respaldo es un secreto público: `AWS Secrets Manager` o rol de instancia, nunca `access_key` en texto plano.
