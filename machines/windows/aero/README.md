---
machine: Aero
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, themebleed, cve-2023-38146, cve-2023-28252]
---

# Aero — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Aero es un Windows 11 con IIS y un repositorio de temas. Un tema `.msstyles` manipulado explota ThemeBleed (CVE-2023-38146) y ejecuta una DLL al previsualizarlo. La escalada usa la vulnerabilidad del kernel de CLFS asociada a Nokoyawa (CVE-2023-28252) para obtener SYSTEM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,3389 <IP>
```

- IIS en 80 y RDP.
- `aero.htb` con secciones de temas y subida.
- `feroxbuster` localiza el panel de carga y archivos `.theme`/`.msstyles`.

## Enumeración

- La aplicación permite subir un tema y previsualizarlo.
- El servidor ejecuta Windows 11 con IIS ARR.
- La versión es vulnerable a ThemeBleed y al fallo de CLFS.
- Se necesita compilar una DLL y un `.msstyles` con la ruta UNC adecuada.

## Foothold

Se crea un tema que referencia un `.msstyles` malicioso; al cargarlo, Windows resuelve una ruta UNC y descarga una DLL controlada. La DLL se ejecuta en el contexto del usuario que previsualiza el tema, lo que entrega una shell.

```powershell
# Compilar la DLL y alojarla en el recurso UNC
# Subir el .theme y solicitar la previsualización
```

## Escalada de privilegios

La shell inicial no es administrativa. Se enumera el parche de CLFS y se usa el exploit de CVE-2023-28252 para corromper el archivo de log y ejecutar código como SYSTEM. La variante pública de Nokoyawa requiere construir y ejecutar el exploit local.

```powershell
systeminfo
whoami /priv
```

## Evidencia

- Tema y `.msstyles` aceptados por la aplicación.
- Conexión UNC y carga de la DLL.
- `whoami` como usuario de IIS.
- `whoami` como `nt authority\system` tras el exploit de CLFS.

## Lecciones aprendidas

- Los temas son código nativo que Windows carga al previsualizarse.
- Una ruta UNC en un archivo de tema puede filtrar credenciales o cargar DLL.
- Los fallos de CLFS han sido explotados por ransomware; el parche es crítico.

## Mitigaciones y detección

- Actualizar Windows y bloquear la carga de temas no confiables.
- Deshabilitar la previsualización automática y restringir UNC saliente.
- Alertar de creación de archivos `.msstyles` y de procesos que cargan DLL desde rutas de red.
- Referencias: NVD CVE-2023-38146, CVE-2023-28252, HTB Aero.

## Referencias

- <https://www.hackthebox.com/machines/Aero>
- <https://0xdf.gitlab.io/2023/09/28/htb-aero.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-38146>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-28252>
