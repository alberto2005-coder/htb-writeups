---
sherlock: BOughT
domain: DFIR / Malware Analysis
difficulty: Hard
platform: Hack The Box
evidence: Volcado de memoria y una imagen lógica AD1 de un equipo de segunda mano
tools: [Volatility 2, FTK Imager, Ghidra, CyberChef]
state: Active
tags: [dfir, memory, malware, dga, ddos, persistence, t1547.001]
---

# BOughT — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Active. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Un usuario compra un portátil de segunda mano y, a los pocos días, la conexión a Internet se vuelve inestable y el proveedor avisa de tráfico anómalo. Se entrega la memoria RAM del equipo y una imagen lógica del disco.

## Evidencias

- `memdump.mem`: volcado de memoria.
- `Files.ad1`: imagen lógica AD1 del sistema de ficheros.

```bash
sha256sum memdump.mem Files.ad1
```

## Investigación

### 1. Inventario y triaje

El perfil de memoria se obtiene antes de cualquier plugin:

```bash
vol.py -f memdump.mem imageinfo
```

```text
Suggested Profile(s): Win10x64_19041
```

La captura es del **2023-08-07 21:28:13**. Con el perfil, el árbol de procesos separa lo legítimo de lo añadido:

```bash
vol.py -f memdump.mem --profile=Win10x64_19041 pstree
vol.py -f memdump.mem --profile=Win10x64_19041 cmdline
```

Aparece un proceso **`SecurityCheck`** sin ruta de sistema y con la línea de comandos apuntando a la carpeta de inicio del usuario: persistencia por `StartUp`, sin servicio ni tarea programada.

### 2. Línea temporal

La imagen AD1 se monta con **FTK Imager** y se extrae el binario. Los metadatos del ejecutable dan el SHA-256 de la muestra; la ejecución se fecha con el `$MFT` de la propia imagen.

```text
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\SecurityCheck.exe
```

El binario crea un mutex **`config_m2`**, que es el identificador para comprobar si ya está en ejecución: un mutex único por familia y campaña.

### 3. Artefacto clave

En Ghidra, la función de entrada hace:

```c
Sleep(900000);              /* 15 minutos */
if (IsDebuggerPresent()) exit(0);
```

El `Sleep` retrasa el análisis dinámico y `IsDebuggerPresent` lo aborta si hay depurador: dos barreras baratas que explican por qué el malware "no hace nada" en un sandbox.

Después construye dominios con un **DGA**: cinco niveles de nueve caracteres (`9^5 = 59049` dominios por ejecución). La configuración se lee de `C:\Windows\win.ini` y los comandos de `C:\Users\Public\config.ini`, en base64:

```bash
python3 -c "import base64;print(base64.b64decode(open('config.ini').read()))"
```

El C2 activo en la captura es `http://cl0lr8.xyz`. El comportamiento DDoS consiste en `ping -n 16` y ráfagas de 20 peticiones GET: ruido de volumen bajo, pero suficiente para que el proveedor lo note.

## Conclusiones

- El equipo llegó comprometido: la persistencia está en la carpeta `StartUp` del usuario, no en un mecanismo del sistema.
- El binario se protege con retardo y comprobación de depurador, y usa un DGA de 59.049 dominios para sobrevivir al bloqueo de uno.
- La configuración vive en dos rutas poco sospechosas (`win.ini`, `Public\config.ini`), lo que permite cambiar C2 sin recompilar.

## Lecciones

- `pstree` + `cmdline` resuelven más casos que cualquier firma: la ruta del proceso delata la persistencia.
- Un `Sleep` largo no es "malware inactivo": es una decisión de diseño; hay que mirar el código, no solo el comportamiento en 60 segundos.
- `IsDebuggerPresent` se salta con ScyllaHide o parcheando el salto; el análisis estático evita el problema.
- Un mutex conocido permite buscar la misma familia en otros equipos con una regla simple.

## Mitigaciones y detección

- Monitorizar escrituras en `StartUp` de cualquier perfil (Sysmon 11) y ejecuciones desde esa ruta (Sysmon 1).
- Alertar de procesos con nombres de "seguridad" sin firma ni ruta de sistema.
- Bloquear resolución de dominios recién creados y con TTL bajo; el DGA se detecta por volumen de NXDOMAIN, no por nombre.
- Revisar `win.ini` y `C:\Users\Public` como rutas de configuración anómalas en los escaneos de integridad.

MITRE: T1547.001 (registry run keys / startup folder), T1498 (network denial of service), T1568.002 (domain generation algorithms), T1497.001 (virtualization/sandbox evasion).

## Referencias

- <https://mwalkowski.com/post/sherlock-bought>
- <https://github.com/volatilityfoundation/volatility>
- <https://learn.microsoft.com/en-us/sysinternals/downloads/autoruns>
