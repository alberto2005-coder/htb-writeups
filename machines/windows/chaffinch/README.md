---
machine: Chaffinch
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, geoserver, cve-2024-36401, csc, privesc]
---

# Chaffinch — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un GeoServer expuesto es vulnerable a CVE-2024-36401: una expresión XPath en un parámetro OGC ejecuta código sin autenticación. La shell permite enumerar el sistema y encontrar credenciales o configuraciones del servicio CSC de Windows. El abuso del servicio de caché de credenciales (CSC) permite escalar a un usuario con más privilegios y completar la máquina.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443,3389 <IP>
```

- IIS/GeoServer y RDP.
- `chaffinch.htb` con la consola web de GeoServer.
- La versión y el endpoint WFS confirman el componente vulnerable.

## Enumeración

- GeoServer expone `/geoserver/web/` y servicios OGC.
- La versión es anterior a 2.22.6/2.23.6/2.24.4/2.25.2.
- El usuario del servicio y los archivos de configuración son accesibles tras la ejecución.
- Se revisan tareas, servicios y credenciales locales.

## Foothold

Se envía una petición WFS con un nombre de propiedad manipulado que GeoTools evalúa como XPath. La expresión ejecuta un comando y devuelve una reverse shell como el usuario del servicio.

```bash
curl -s 'http://<IP>/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=...'
```

## Escalada de privilegios

La shell permite leer la configuración y localizar el servicio CSC. Se abusa de la caché de credenciales de Windows para obtener o modificar un hash de usuario con privilegios y autenticarse como administrador. La técnica exacta depende de los artefactos disponibles; la ficha separa la enumeración del abuso.

```powershell
whoami /all
Get-Service | Where-Object Name -like '*CSC*'
```

## Evidencia

- Respuesta de GeoServer con el comando ejecutado.
- `whoami` como usuario del servicio.
- Configuración y servicios locales enumerados.
- Acceso administrativo tras el abuso de CSC.

## Lecciones aprendidas

- GeoServer debe actualizarse y no exponerse a Internet.
- Las expresiones de propiedades no son datos inertes.
- Los servicios de caché de credenciales son un objetivo de escalada.

## Mitigaciones y detección

- Actualizar GeoServer a una versión corregida y limitar `/geoserver`.
- Ejecutar el servicio con una cuenta de bajo privilegio.
- Monitorizar peticiones WFS con expresiones y accesos anómalos a CSC.
- Referencias: NVD CVE-2024-36401, HTB Chaffinch, Microsoft CSC.

## Referencias

- <https://www.hackthebox.com/machines/Chaffinch>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-36401>
- <https://geoserver.org/vulnerability/2024/09/12/cve-2024-36401.html>
- <https://attack.mitre.org/techniques/T1190/>
