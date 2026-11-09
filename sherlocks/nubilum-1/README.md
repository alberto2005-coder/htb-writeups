---
sherlock: Nubilum-1
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
evidence: Logs de CloudTrail, artefactos de una EC2 y copia de S3
tools: [jq, AWS CLI, CyberChef, Elastic]
---

# Nubilum-1 — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Amazon avisa de que una **EC2** del entorno se usa con fines maliciosos. El administrador de nube recuerda haber visto más instancias de las que desplegó. Se entrega la entrevista de triaje, los logs de **CloudTrail** y una captura de la instancia comprometida.

## Evidencia

- `CloudTrail/` con los JSON de la actividad de la cuenta.
- `catscale_*.tar.gz` con artefactos recogidos de la instancia.
- `forela-storage/` (copia del bucket), `unusual-directory.zip` e `interview.txt`.

## Método

1. **Normalizar** los eventos y quedarse con las llamadas de escritura.

```bash
jq -r '[.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress]|@tsv' CloudTrail/*.json | sort | head
```

2. **Línea base**: qué usuarios y roles crean recursos (`RunInstances`, `CreateKeyPair`, `CreateUser`, `AttachUserPolicy`). Lo que no encaja con la entrevista es del atacante.

3. **IP de origen** y ventana temporal: agrupar por `sourceIPAddress` y contar acciones por hora.

4. **Instancia**: en el `tar.gz` de CatScale se ven procesos, conexiones y ficheros; `unusual-directory.zip` suele contener el **implante**.

5. **Persistencia**: comprobar si se crearon claves de acceso, usuarios o políticas nuevas que mantengan el acceso tras el borrado de la instancia.

## Qué enseña

- CloudTrail es el "PCAP" de la nube: quién, qué, cuándo y desde dónde.
- El abuso de nube empieza por crear recursos (minería, C2) con credenciales robadas.
- La entrevista al administrador es evidencia: define la línea base.
- Borrar una instancia no revoca claves creadas antes.

## Tropiezos

- **Volumen**: filtrar por `eventName` y `errorCode` antes de leer.
- **Roles frente a usuarios**: la identidad efectiva puede ser un rol asumido; seguir `sessionIssuer`.
- **Zonas horarias**: CloudTrail va en UTC; la entrevista, no.
