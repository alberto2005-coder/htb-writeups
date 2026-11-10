---
sherlock: Loggy
domain: Análisis de malware
difficulty: Easy
platform: Hack The Box
evidence: Binario Go, keylog y capturas de una máquina comprometida
tools: [Ghidra, strings, CyberChef, readpe]
state: Retired
tags: [dfir, malware, go, keylogger, ftp, exfiltracion]
---

# Loggy — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Janice, de contabilidad, fue avisada por el SOC: sus credenciales corporativas aparecen en la dark web. Se recuperan ficheros de su equipo y se envían al analista de REM. Hay que reconstruir qué hizo el binario, qué robó y a dónde lo envió.

## Evidencias

- `Loggy.exe`: PE32+ x86-64, 6,5 MB, MD5 `215e79eaa7b9ac16a7d2bce15c94b8de`.
- La captura de pantalla y el fichero de keylog generados en el equipo.

## Investigación

1. **Triage**: hash, tipo y compilador.

```bash
sha256sum Loggy.exe; file Loggy.exe
strings -n 8 Loggy.exe | grep -i "go1\." | head
```

El binario está escrito en **Go**: se reconoce por el runtime y las rutas `go/pkg/mod`. Eso cambia el enfoque (Ghidra + `strings`, sin importaciones de Windows al uso).

2. **Capacidades**: buscando dependencias en las cadenas aparecen dos repositorios reveladores:

```bash
strings Loggy.exe | grep -i github
# github.com/kbinani/screenshot   -> capturas de pantalla
# github.com/jlaffaye/ftp         -> cliente FTP
```

3. **Keylogger**: el binario intercepta el teclado y **añade** las pulsaciones a `keylog.txt`. Ahí queda el cambio de contraseña de Janice, que es como se filtran las credenciales.

4. **Exfiltración**: `sendFilesViaFTP` se conecta con credenciales **hardcodeadas** a un servidor externo y sube las capturas y el keylog.

```bash
strings Loggy.exe | grep -E ":21"
# <host>:21
```

5. **IOCs**: host de exfiltración, credenciales del atacante, rutas de los ficheros generados y nombres de los repositorios usados como firma.

## Hallazgos

- Keylogger + capturas de pantalla en Go, con exfiltración por **FTP en claro** al puerto 21.
- Persistencia innecesaria: el daño es el robo de credenciales, no el cifrado.
- El binario lleva las credenciales del atacante embebidas, lo que permite atribuir la infraestructura.

## Lecciones

- En binarios Go, las rutas de módulos son una lista de capacidades gratis.
- Un keylog en texto plano en el perfil del usuario es evidencia directa de credenciales robadas.
- FTP de salida desde un puesto de usuario es una señal de exfiltración que casi ningún filtrado bloquea.

## Tropiezos

- **Buscar importaciones clásicas**: en Go no hay `Import Address Table` útil; hay que leer cadenas y funciones.
- **Ejecutar la muestra**: sólo en VM aislada; aquí basta el análisis estático.
- **Confundir el host con la URL**: el dial lleva el puerto (`:21`); la respuesta es sólo el dominio.
