---
title: HTML smuggling y HTA — el archivo que se construye en el navegador
tags: [forensics, windows, html-smuggling, hta, dll-sideloading, phishing]
---

# HTML smuggling y HTA: el payload que no viaja como adjunto

[🇬🇧 English](html-smuggling-hta.en.md) | **Español**

## 1. Por qué evade el filtro

Un correo con un `.exe` o un ZIP sospechoso se bloquea. En **HTML smuggling**, el adjunto es un `.html` con JavaScript que decodifica un blob Base64, crea un `Blob` y fuerza la descarga de un ZIP/EXE. El archivo malicioso nunca se solicita al servidor: se genera en el navegador.

```html
<script>
const b64 = "<BASE64>";
const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
const blob = new Blob([bytes], {type: "application/octet-stream"});
const a = document.createElement("a");
a.href = URL.createObjectURL(blob);
a.download = "invoice.zip";
a.click();
</script>
```

El proxy ve HTML y JavaScript; el ZIP solo existe en el disco del usuario.

## 2. HTA

Un **HTA** (HTML Application) se ejecuta con `mshta.exe`, un binario firmado de Windows. Puede contener VBScript/JScript y lanzar procesos:

```html
<html><head><script language="VBScript">
CreateObject("WScript.Shell").Run "msoev.exe", 0, False
</script></head></html>
```

`mshta.exe` es un **LOLBin**: si la política lo permite, ejecuta el HTA sin descargar un ejecutable adicional. Se invoca con doble clic o desde otro script.

## 3. Cadena típica

```text
correo → downloader.html → ZIP → sheet.hta → mshta.exe
      → msoev.exe (señuelo) → mso.dll / AppVIsvSubsystems64.dll
      → EmpireClient.exe → C2
```

- El PDF o la factura es el señuelo.
- El EXE legítimo se coloca junto a una DLL maliciosa con el nombre que espera (**DLL side-loading**).
- La DLL carga el stager y este abre el canal de mando.

## 4. Análisis forense

- **Procmon**: `Process Name is mshta.exe` y `Operation is Load Image`; luego `msoev.exe` y las DLL desde `Downloads`/`Temp`.
- **pcap**: DNS, SNI, POST periódicos; el `User-Agent` y la ruta importan más que la IP.
- **Descargas**: historial del navegador, Zone.Identifier y `%TEMP%`.
- **Persistencia**: Run keys, tareas, servicios y copias del payload.
- **Hash**: del HTML, del ZIP, del HTA y de las DLL; se correlacionan con otros equipos.

## 5. Detección

- HTML con blobs Base64 grandes y `a.download`.
- `mshta.exe` con un argumento en `Downloads`, `Temp` o una URL.
- DLL cargadas desde rutas de usuario por procesos firmados.
- Conexiones periódicas desde un proceso hijo de Office/navegador.
- Eventos de SmartScreen/Defender y creación de tareas.

## 6. Mitigación

- Bloquear `mshta.exe` con AppLocker/WDAC salvo excepción.
- Inspeccionar HTML y JavaScript, no solo adjuntos PE.
- Forzar Mark-of-the-Web y SmartScreen; no permitir ejecución desde `Downloads`.
- Reglas de side-loading: DLL solo desde `System32` o el directorio de la aplicación.
- Segmentar y monitorizar C2; aislar el host y rotar credenciales.

MITRE: T1027.006, T1218.005, T1574.002, T1071.001.

## 7. Referencias

- <https://attack.mitre.org/techniques/T1027/006/>
- <https://attack.mitre.org/techniques/T1218/005/>
- <https://0xdf.gitlab.io/2024/05/02/htb-sherlock-einladen.html>
