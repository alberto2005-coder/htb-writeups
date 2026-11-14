---
sherlock: EasyMoney
category: Malware Analysis
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware-analysis, windows, lnk, yandex, certutil]
---

# EasyMoney — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un usuario descarga un supuesto sorteo de dinero y ejecuta un acceso directo. Días después, el equipo muestra persistencia y tráfico hacia un C2. Se entrega el perfil del usuario, los registros de PowerShell y los archivos descargados.

## Evidencias

- `2025-GiveAways.lnk` y su `customDestinations-ms`.
- Historial de PowerShell y caché de `certutil`.
- `wldp.dll`, `yanda.tmp` y el árbol de `%LOCALAPPDATA%`.

```bash
sha256sum 2025-GiveAways.lnk
LECmd.exe -f 2025-GiveAways.lnk
```

## Investigación

### 1. Inventario y triaje

`LECmd` muestra que el LNK apunta a PowerShell ISE y lanza un comando con una URL. El nombre del archivo simula un sorteo. Se revisan descargas, prefetch y procesos hijos para confirmar la ejecución.

```bash
JLECmd.exe -f customDestinations-ms --csv out
```

### 2. Línea temporal

El LNK ejecuta PowerShell, que enumera paquetes y descarga una DLL con `certutil`. La DLL se coloca junto a un navegador Yandex vulnerable a búsqueda de DLL. Al abrir el navegador, `wldp.dll` carga el payload y establece el C2.

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational'
```

### 3. Artefacto clave

La caché de `CryptnetUrlCache` conserva el binario descargado. El nombre del mutex y la ruta de `yanda.tmp` aparecen en el análisis del ejecutable. La combinación confirma el sideloading y el framework de C2.

## Conclusiones

- El acceso inicial fue un LNK de phishing.
- `certutil` se usó para descargar la DLL maliciosa.
- El sideloading de Yandex ejecutó el payload.
- El C2 y el mutex son IOC de alta confianza.

## Lecciones

- Los LNK pueden lanzar PowerShell sin un ejecutable visible.
- `certutil` sigue siendo un LOLBin para descargas.
- La caché de criptografía conserva archivos descargados.
- El sideloading aprovecha una aplicación legítima.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/luckystars0612/Sherlock-HTB/tree/main/EasyMoney>
- <https://attack.mitre.org/techniques/T1204/002/>
