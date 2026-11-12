---
sherlock: Conned-Again
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, confluence, cve-2023-22515, cve-2023-22527]
---

# Conned-Again — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.
> Evidencias descritas a partir del escenario público y de writeups técnicos; no se publican datos del entorno.

## Escenario

El servidor Confluence de Forela ha sido comprometido. Se entrega un triaje **CatScale** del host Linux y hay que reconstruir cómo el atacante obtuvo acceso administrativo, qué modificó y si desplegó persistencia. El caso gira alrededor de dos CVEs de Confluence: **CVE-2023-22515** (creación no autorizada de administradores) y **CVE-2023-22527** (inyección OGNL en plantillas).

## Evidencias

- Archivo de triaje CatScale con el sistema de ficheros de la instalación.
- Logs de Confluence, Tomcat y del proxy delante de la aplicación.
- Configuración de la instancia (`confluence.cfg.xml`, `server.xml`, `web.xml`).
- Metadatos de procesos, usuarios y ficheros creados durante la ventana del incidente.

```bash
sha256sum conned-again.zip
unzip -l conned-again.zip | head -40
```

Antes de abrir nada, se anotan los hashes y se trabaja sobre una copia. Los artefactos pueden contener credenciales: se redactan en las notas.

## Investigación

### 1. Inventario y triaje

Se localiza la versión exacta de Confluence y se compara con las versiones afectadas:

```bash
grep -R "confluence.version\|BuildNumber" opt/atlassian/confluence/ 2>/dev/null | head
grep -R "CVE-2023-2251\|CVE-2023-22527" . 2>/dev/null | head
```

También se revisa qué usuario ejecuta el servicio y desde qué directorio se sirve la aplicación. Un Confluence expuesto directamente a Internet y sin proxy autenticado es el escenario de riesgo.

### 2. Línea temporal

La fuente principal son los access logs y los logs de Confluence. Se busca:

```bash
grep -E "setupadministrator|setup/setup|text-inline|template/aui" logs/*.log | head -50
```

- Peticiones a `/setup/setupadministrator.action` fuera de la instalación inicial.
- Peticiones a `/template/aui/text-inline.vm` con parámetros OGNL.
- Creación de usuarios administradores y cambios en `cwd_user`.
- Reinicios del servicio y despliegue de ficheros JSP.

Se normalizan las horas: los logs de Confluence suelen estar en la zona del servidor, mientras que el proxy puede registrar UTC. La diferencia debe explicarse antes de ordenar eventos.

### 3. Artefacto clave

El punto que resuelve el caso es la secuencia de dos peticiones: una que crea o eleva una cuenta administrativa y otra que ejecuta OGNL en la plantilla. En el sistema de ficheros se busca el efecto:

```bash
grep -R "Runtime\|getRuntime\|ProcessBuilder" opt/atlassian/confluence/ 2>/dev/null | head
find . -name '*.jsp' -newermt '<START>' ! -newermt '<END>' 2>/dev/null
```

Un JSP nuevo en el directorio de trabajo, un usuario administrador no reconocido o una tarea programada creada justo después de la petición confirman la ejecución. La ausencia de un JSP no descarta el ataque: el OGNL puede ejecutar comandos en memoria.

## Conclusiones

- El atacante explotó una instancia de Confluence vulnerable y creó acceso administrativo.
- La ejecución de comandos se produjo en el contexto del usuario del servicio, no como root.
- Los IOCs principales son las rutas de las dos CVEs, el User-Agent y la IP de origen, y los usuarios creados fuera del alta corporativa.
- Cualquier credencial visible en la configuración debe rotarse.

## Lecciones

- Un Confluence expuesto debe tener proxy, autenticación y reglas que bloqueen `/setup/*` después de la instalación.
- Actualizar no basta si quedan cuentas administrativas creadas por el atacante: hay que revisar `cwd_user` y los permisos.
- Los logs de aplicación y de proxy deben correlacionarse por hora y por identificador de petición.
- Un triaje CatScale conserva el contexto justo para responder “qué cambió”, no solo “qué versión había”.
