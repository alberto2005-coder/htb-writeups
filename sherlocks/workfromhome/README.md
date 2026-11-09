---
sherlock: WorkFromHome
domain: DFIR / Windows
difficulty: Medium
platform: Hack The Box
evidence: Artefactos de un portátil tras robo de credenciales y RDP
tools: [KAPE, MFTECmd, Timeline Explorer, Eric Zimmerman tools]
state: Retired
tags: [dfir, dfir-/-windows]
---


# WorkFromHome — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un empleado en remoto cae en una **web de phishing** que imita el login corporativo y entrega sus credenciales. El atacante entra por **RDP**, abusa de un privilegio de gestión de volúmenes, planta un **DLL malicioso** y se asegura persistencia secuestrando el flujo de **WMI**.

## Evidencias

- Perfil de usuario: historial de navegador, `UserAssist`, *jump lists*, `ConsoleHost_history`.
- `$MFT`, **SRUM**, logs de **WMI**, de **Defender** y visor de eventos.

## Investigación

1. **Entrada**: historial de Chrome/Edge → URL de phishing y hora. El `Referer` y el patrón de la URL confirman el robo de credenciales.

2. **RDP**: eventos de inicio de sesión (4624 tipo 10) y artefactos de GUI (`UserAssist`, recientes) muestran qué hizo el intruso en la sesión.

3. **Privilegio**: con `whoami /priv` el atacante descubre un privilegio de gestión de volúmenes (**SeManageVolumePrivilege**), que permite escribir en rutas protegidas.

4. **DLL**: un `PrintConfig.dll` (o similar) se descarga con `certutil` —LOLBIN— y se coloca en una ruta de búsqueda de `wmiprvse.exe`.

5. **Persistencia**: el *search order hijacking* hace que `wmiprvse.exe` cargue la DLL cada vez que se usa WMI (T1574.001). Verificar en SRUM/Defender el proceso y el momento.

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- Un privilegio "de administración de discos" puede ser escritura arbitraria en `C:\Windows`.
- `certutil` sigue siendo el descargador favorito: LOLBIN firmado y permitido.
- Secuestrar el orden de búsqueda de DLL en un proceso de sistema da persistencia sin servicios nuevos.
- La correlación navegador → RDP → MFT → SRUM construye la historia completa.

## Tropiezos

- **MFT no es un log**: una entrada puede reutilizarse; para el "cuándo" exacto, cruzar con SRUM y eventos.
- **DLL con nombre legítimo**: el nombre no delata; la ruta y el proceso que la carga sí.
- **Prefetch ausente**: en Windows 10/11 puede estar deshabilitado; no concluir que no se ejecutó.
