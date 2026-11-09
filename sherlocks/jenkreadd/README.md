---
title: JenkreadD
category: DFIR / Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, jenkins, cve-2024-23897, file-read, logs]
sherlock: JenkreadD
domain: DFIR
---


# JenkreadD — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

## Escenario

Un servidor **Jenkins** expuesto a Internet ha sido sondeado. La evidencia incluye logs del servicio, el historial de accesos y artefactos del host. Hay que determinar si se explotó la lectura arbitraria de ficheros de la CLI (**CVE-2024-23897**) y qué se llevó el atacante.

## Evidencias

```bash
ls -la; grep -a "jenkins" *.log | head
EvtxECmd.exe -d . --csv out --csvf evtx.csv     # si hay EVTX
```

Artefactos útiles: `jenkins.log`, `access_log`, `audit.log`, el directorio `$JENKINS_HOME/logs`, tareas programadas y el historial de shell del servicio.

## Investigación

- **CVE-2024-23897**: la CLI (`jenkins-cli.jar`) interpreta argumentos que empiezan por `@` como rutas de fichero; un error devuelve líneas del fichero. En los logs se ven peticiones a `/cli` con parámetros `@/etc/passwd`, `@/var/jenkins_home/secrets/...` o similares.
- Buscar en `access_log` peticiones **POST /cli** con `-webSocket` o `args4j` y códigos 200/500 seguidos de descargas grandes.
- Revisar el log de auditoría de Jenkins: creación de usuarios, cambios de credenciales y ejecución de jobs.
- Si hay EVTX/Sysmon, cruzar **4688** con `java -jar jenkins-cli.jar` y **Sysmon 11** con ficheros nuevos.
- Confirmar qué ficheros se leyeron: claves de `secrets/`, `credentials.xml` y `config.xml` permiten RCE posterior.

## Conclusiones

```text
POST /cli  args="@<ruta>"  status=500
jenkins.log: "No such file" + primera línea del fichero
audit.log: usuario nuevo / job creado
```

El patrón `@ruta` + error con contenido es la firma del CVE; un job nuevo o un usuario creado confirma el impacto.

## Lecciones

- La lectura arbitraria de ficheros en Jenkins suele terminar en RCE: `secrets/` y las credenciales están ahí.
- Los logs de la CLI son la evidencia principal; el error que revela el fichero queda registrado.
- Comparar el volumen de peticiones con la línea base separa escaneo de explotación.

- Actualizar Jenkins (CVE-2024-23897) y deshabilitar la CLI remota si no se usa.
- Autenticación obligatoria, `authorizationStrategy` mínima y segmentación del panel.
- Alertar de `POST /cli` con `@` y de errores 500 repetidos.
- Rotar credenciales y claves de `secrets/` tras una exposición.

MITRE: T1190, T1005, T1059.
