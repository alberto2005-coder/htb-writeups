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

- Entrada: phishing que imita el login corporativo; las credenciales se usan por **RDP** (4624 tipo 10), así que la sesión del atacante es interactiva desde el primer minuto.
- El privilegio clave es **`SeManageVolumePrivilege`** en la cuenta de Otello: permite operaciones a nivel de volumen y escribir en rutas protegidas.
- La DLL legítima **`PrintConfig.dll`** se sustituye por una maliciosa descargada con `certutil`, en una ruta de búsqueda de `wmiprvse.exe`: *search order hijacking* (T1574.001) con persistencia vía WMI.

## Lecciones

- El historial del navegador y `UserAssist` fechan el clic en el phishing mejor que el log de Defender.
- `SeManageVolumePrivilege` parece innocuo y da escritura donde no debería: revisar privilegios, no solo grupos.
- La sustitución de una DLL de Windows por nombre es invisible para el usuario: solo SRUM/Defender y el hash la delatan.

- El orden correcto es navegador → RDP → privilegios → DLL → WMI; saltarse el historial deja la entrada sin explicar.
- `SeManageVolumePrivilege` no aparece en las guías de escalada habituales y aquí es el pivote.
- Comparar el hash de `PrintConfig.dll` con el de la instalación limpia confirma la sustitución.

## Qué enseña

- Un privilegio "de administración de discos" puede ser escritura arbitraria en `C:\Windows`.
- `certutil` sigue siendo el descargador favorito: LOLBIN firmado y permitido.
- Secuestrar el orden de búsqueda de DLL en un proceso de sistema da persistencia sin servicios nuevos.
- La correlación navegador → RDP → MFT → SRUM construye la historia completa.

## Tropiezos

- **MFT no es un log**: una entrada puede reutilizarse; para el "cuándo" exacto, cruzar con SRUM y eventos.
- **DLL con nombre legítimo**: el nombre no delata; la ruta y el proceso que la carga sí.
- **Prefetch ausente**: en Windows 10/11 puede estar deshabilitado; no concluir que no se ejecutó.
