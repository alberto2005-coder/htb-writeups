---
sherlock: Heartbreaker
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, outlook, kape, mft, browser-forensics]
---

# Heartbreaker — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales de la plataforma.

## Escenario

Se entrega un triaje KAPE de una estación Windows (`wb-ws-01`) relacionada con una intrusión. Hay que reconstruir el correo de phishing, la ejecución del adjunto, la actividad del navegador y la posible exfiltración. Es el primer caso de la saga Heartbreaker; no debe confundirse con Continuum ni Denouement.

## Evidencias

- Triaje KAPE con `$MFT`, EVTX y artefactos de usuario.
- Buzón de Outlook en formato OST/PST.
- Historial y descargas del navegador (SQLite).
- Configuración y logs de WinSCP.
- Prefetch, Amcache y elementos de inicio.

```bash
sha256sum heartbreaker.zip
unzip -l heartbreaker.zip | head -40
```

Se trabaja sobre copia y con la zona horaria documentada. Los artefactos pueden contener credenciales; se redactan.

## Investigación

### 1. Inventario y triaje

Se localiza el perfil y se ordenan las fuentes por valor temporal:

```text
C/Users/<USER>/NTUSER.DAT
C/Users/<USER>/AppData/Local/Microsoft/Windows/Explorer
C/Users/<USER>/AppData/Roaming/Microsoft/Windows/Recent
C/Windows/System32/winevt/Logs
C/$MFT
```

El OST se parsea con `libpff`/`readpst` o una herramienta de correo forense. Se buscan adjuntos ejecutables, macros y URLs.

### 2. Línea temporal

Se cruzan:

- Fecha de recepción del correo y nombre del adjunto.
- Creación del fichero en `Downloads` y ejecución en Prefetch.
- Eventos 4688/Sysmon 1 y conexiones de red.
- Historial de navegación y descargas posteriores.
- Actividad de WinSCP (sesiones, hosts, ficheros transferidos).

```bash
MFTECmd.exe -f '$MFT' --csv mft.csv
PECmd.exe -d Prefetch --csv prefetch.csv
```

### 3. Artefacto clave

La cadena se confirma cuando el adjunto del correo coincide por nombre/hash con el fichero descargado y ejecutado, y la primera conexión de red ocurre segundos después. WinSCP aporta la prueba de exfiltración si hay una sesión hacia un host externo con transferencia de archivos.

```text
correo -> adjunto -> Downloads -> Prefetch -> conexión -> WinSCP
```

## Conclusiones

- El acceso inicial fue un correo con un adjunto malicioso.
- El ejecutable se lanzó desde el perfil del usuario y estableció conexión con un C2.
- La exfiltración se hizo por un canal interactivo (WinSCP/SFTP) o HTTP.
- Los IOCs incluyen remitente, asunto, nombre/hash del adjunto, dominio/IP y rutas.

## Lecciones

- El OST conserva el correo original y el adjunto aunque el usuario lo borre.
- Prefetch y MFT dan la ejecución; el correo da el origen.
- WinSCP guarda hosts, usuarios y rutas de forma recuperable.
- La correlación de tres fuentes evita atribuir una descarga legítima al atacante.

## Referencias

- <https://mwalkowski.com/post/sherlock-heartbreaker>
- <https://learn.microsoft.com/en-us/outlook/troubleshoot/data-files/ost-file>
- <https://attack.mitre.org/techniques/T1566/001/>
