---
sherlock: Exitiabilis
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, elk, vpn, siem]
---

# Exitiabilis — Hack The Box

[🔤 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

El SOC de una empresa ha detectado actividad anómala en su entorno Windows. Se entrega acceso a un **HELK** (ELK orientado a hunting) con telemetría de endpoints, eventos de Windows y registros de VPN. La hipótesis es que un acceso remoto legítimo, Cisco AnyConnect, se usó como puerta de entrada y desde ahí el atacante se movió por la red. Hay que reconstruir el acceso, la ejecución y la persistencia.

## Evidencias

- Índices de HELK/Kibana con eventos de Windows y Sysmon.
- Logs de autenticación VPN de Cisco AnyConnect.
- Eventos de seguridad del DC y de los equipos afectados.
- Procesos, servicios y conexiones de red dentro de la ventana del incidente.

```bash
# Exportar los índices relevantes desde Kibana/Elasticsearch
curl -s 'http://<HELK>:9200/_cat/indices?v'
```

Se documenta el rango temporal y la zona horaria antes de correlacionar. En un HELK, los índices pueden mezclar `winlogbeat`, `sysmon` y fuentes personalizadas.

## Investigación

### 1. Inventario y triaje

Se identifica qué usuarios y hosts tienen eventos en la ventana. Se empieza por la VPN, porque una autenticación remota exitosa explica cómo entró el atacante sin pasar por la oficina.

```text
event.dataset: *vpn* and event.outcome: success
```

Se revisan:

- Usuario, IP pública y hora de inicio/fin de sesión.
- País o ASN de la IP, comparado con el histórico del usuario.
- Dispositivo y perfil de AnyConnect.
- Intentos fallidos previos y cuentas bloqueadas.

### 2. Línea temporal

Se cruzan tres fuentes:

1. **VPN:** hora de conexión, usuario, IP y duración.
2. **Windows Security:** 4624 (logon), 4625 (failed logon), 4648 (explicit credentials), 4672 (special privileges).
3. **Sysmon:** creación de procesos (1), conexiones de red (3), creación de servicios (7045) y cambios de fichero.

```text
event.code: (4624 or 4625 or 4648 or 4672 or 7045)
```

La hora de la VPN suele estar en UTC; los eventos de Windows pueden estar en hora local. Se normaliza todo a UTC y se marca la diferencia. Un logon tipo 3 o 10 desde la IP VPN, seguido de un proceso hijo inusual, es la primera correlación sólida.

### 3. Artefacto clave

El artefacto que resuelve el caso es la cadena de ejecución posterior al logon: un proceso interactivo (`powershell.exe`, `cmd.exe` o un binario renombrado) que descarga o ejecuta una herramienta, y un servicio o tarea creada para persistir. En HELK se filtra por el host y por el usuario de la VPN, no por la IP sola, porque la IP puede ser compartida.

```text
host.name: <HOST> and user.name: <USER>
```

Se revisa el árbol de procesos y se compara con la línea base del equipo. Un `svchost.exe` con ruta fuera de `System32`, un servicio con binario en `ProgramData` o un `schtasks` recién creado son señales de persistencia.

## Conclusiones

- El acceso inicial fue una sesión VPN válida, probablemente con credenciales comprometidas o reutilizadas.
- Tras el logon, el atacante ejecutó herramientas interactivas y creó persistencia.
- Los IOCs incluyen la IP pública de la VPN, el usuario, el host de destino y los nombres/rutas de los binarios desplegados.
- La ausencia de malware firmado no implica ausencia de intrusión: el abuso de credenciales y herramientas legítimas deja rastro en los logs.

## Lecciones

- La VPN es una superficie de identidad: MFA y correlación de dispositivo son tan importantes como el firewall.
- Un HELK solo es útil si los índices tienen la zona horaria y los campos normalizados.
- Hay que revisar el árbol de procesos, no solo los eventos de autenticación.
- La persistencia mediante servicios o tareas programadas debe alertar por sí sola.
