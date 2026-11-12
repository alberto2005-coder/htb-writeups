---
title: Volatility 3 — análisis de memoria Windows
tags: [forensics, memory, volatility, windows, dfir, malware]
---

# Volatility 3: leer la memoria sin arrancar el equipo

[🇬🇧 English](volatility-memory.en.md) | **Español**

## 1. Antes de analizar

- **Integridad**: calcula SHA-256 del volcado y trabaja sobre una copia. Anota la herramienta de adquisición, la hora y el tamaño.
- **Formato**: `.raw`, `.mem`, `.vmem`, `.dmp` o un snapshot de VMware (`.vmem` + `.vmsn`). El `.vmsn` da contexto, no se analiza como memoria independiente.
- **Símbolos**: Volatility 3 los descarga de Microsoft; en un entorno aislado se usa un *symbol pack* local.

```bash
sha256sum memory.raw
python3 -m venv venv && source venv/bin/activate
pip install volatility3
vol -f memory.raw windows.info
```

Si `windows.info` falla, el perfil no está identificado o el volcado está corrupto. No sigas con plugins que dependen del perfil.

## 2. Procesos y línea de comandos

```bash
vol -f memory.raw windows.pslist
vol -f memory.raw windows.pstree
vol -f memory.raw windows.cmdline
vol -f memory.raw windows.getsids
```

- Compara `pslist` con `psscan` (procesos terminados o ocultos).
- Un PPID incoherente delata inyección o *process hollowing*.
- `cmdline` es la fuente más rica: PowerShell codificado, `rundll32`, rutas en `Temp`.

```bash
vol -f memory.raw windows.psscan | grep -iE 'powershell|rundll32|svchost'
```

## 3. Red

```bash
vol -f memory.raw windows.netscan
vol -f memory.raw windows.netstat
```

Se correlaciona PID, IP remota, puerto y estado. Un proceso de usuario con conexión a un puerto externo sin navegador asociado es sospechoso. En un volcado antiguo, `netscan` puede no ver conexiones ya cerradas.

## 4. Código inyectado

```bash
vol -f memory.raw windows.malfind
vol -f memory.raw windows.vadinfo --pid <PID>
vol -f memory.raw windows.malfind --dump --pid <PID>
```

`malfind` busca regiones `PAGE_EXECUTE_READWRITE` sin fichero de respaldo y con cabecera MZ. No todas son maliciosas (JIT, .NET). Se confirma volcando y mirando cadenas, imports y entropía.

```bash
strings -a <dump>.dmp | grep -iE 'http|cmd|powershell|flag'
```

## 5. Ficheros y registro

```bash
vol -f memory.raw windows.filescan | grep -iE 'temp|download|\.ps1|\.exe'
vol -f memory.raw windows.dumpfiles --virtaddr <OFFSET>
vol -f memory.raw windows.registry.hivelist
vol -f memory.raw windows.registry.printkey --key 'Software\Microsoft\Windows\CurrentVersion\Run'
vol -f memory.raw windows.hashdump
```

- `dumpfiles` recupera el contenido si sigue en la caché.
- `hashdump` extrae hashes locales; no se publican.
- Las Run keys y los servicios dan persistencia.

## 6. Línea temporal

```bash
vol -f memory.raw timeliner --output-file timeline.csv
```

Combina procesos, ficheros y conexiones. Normaliza todo a UTC y contrasta con EVTX/Prefetch del disco. La memoria sola no prueba la secuencia completa.

## 7. Límites y errores típicos

- **Símbolos incorrectos** → plugins vacíos o erróneos; fija la versión.
- **`malfind` como veredicto** → es una pista, no una prueba.
- **Volcado parcial** → la ausencia de un proceso no significa que no existiera.
- **Hora local** → convierte a UTC antes de correlacionar.
- **Hashes publicados** → nunca; son credenciales.

## 8. Detección y respuesta

- Capturar memoria antes de apagar o reiniciar.
- Aislar el host y preservar el volcado con hash.
- Correlacionar memoria con EVTX, Prefetch y telemetría de red.
- Documentar cadena de custodia y limitaciones.

MITRE: T1055, T1059.001, T1105, T1547.

## 9. Referencias

- <https://github.com/volatilityfoundation/volatility3>
- <https://volatility3.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1055/>
