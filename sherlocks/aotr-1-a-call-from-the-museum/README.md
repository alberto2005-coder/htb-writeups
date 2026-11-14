---
sherlock: "AoTR 1: A Call from the Museum"
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, email, lnk, powershell, registry]
---

# AoTR 1: A Call from the Museum — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una empleada de un museo recibe un correo sobre una exposición internacional y abre un archivo adjunto. Poco después, el equipo muestra actividad anómala. Se entrega el correo y los artefactos del usuario para reconstruir el acceso inicial.

## Evidencias

- `URGENT_Updated_Health_&_Customs_Compliance_for_Cross-Border_Festive_Event.eml`.
- Un acceso directo `.lnk` y un script de PowerShell.
- Colmena `NTUSER.DAT` y archivos de `%TEMP%`.

```bash
sha256sum *.eml *.lnk
file *
```

## Investigación

### 1. Inventario y triaje

Se revisan las cabeceras del correo: remitente, `Return-Path`, `Message-ID`, servidores y enlaces. El adjunto es un LNK que simula un PDF y apunta a un ejecutable legítimo con argumentos controlados.

```bash
head -40 urgent.eml
exiftool urgent.eml
```

### 2. Línea temporal

El LNK se ejecuta y lanza PowerShell con una cadena codificada. El script consulta el `MachineGuid` del registro, envía datos a un dominio y descarga una segunda etapa. Se ordenan los artefactos por hora y se identifica el primer proceso malicioso.

```powershell
Get-Content .\script.ps1
```

### 3. Artefacto clave

La clave `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` aparece en el script y permite identificar el equipo víctima. El dominio de C2 y la ruta del segundo payload se obtienen al desofuscar la concatenación de cadenas.

## Conclusiones

- El acceso inicial fue un LNK malicioso enviado por correo.
- PowerShell se usó para reconocimiento y descarga.
- El `MachineGuid` sirvió como identificador de la víctima.
- El C2 y el segundo payload deben bloquearse y buscarse en otros equipos.

## Lecciones

- Los LNK pueden disfrazarse de documentos.
- El historial de PowerShell y el registro complementan el correo.
- Un `.eml` conserva cabeceras y adjuntos para el análisis.
- Los dominios recién registrados son un indicador útil.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://medium.com/@annisaep/hack-the-box-aotr-a-call-from-the-museum-write-up-457926888768>
- <https://attack.mitre.org/techniques/T1204/002/>
