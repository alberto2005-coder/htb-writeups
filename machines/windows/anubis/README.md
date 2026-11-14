---
machine: Anubis
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, asp, jamovi, adcs, pkinit, active-directory]
---

# Anubis — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una inyección ASP en una aplicación pública da una shell en un contenedor Windows. Desde ahí se alcanza una aplicación interna que puede enviar peticiones a un Responder controlado y filtrar credenciales. Con acceso SMB se sube un archivo Jamovi malicioso, se obtiene una shell en el host y se abusa de una plantilla ADCS con PKINIT para llegar a Administrator.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443,445,3389 <IP>
```

- IIS/ASP, SMB, RDP y servicios internos.
- La aplicación pública tiene un formulario vulnerable.
- El dominio y los controladores se enumeran desde el contenedor.

## Enumeración

- La inyección ASP ejecuta comandos en el contenedor.
- Se enumeran redes, usuarios y recursos internos.
- Una aplicación interna acepta URLs y es vulnerable a SSRF.
- Responder captura credenciales de dominio.
- El recurso SMB contiene o acepta archivos Jamovi.

## Foothold

Se explota la inyección ASP para obtener una shell en el contenedor. Se pivota a la aplicación interna y se usa SSRF para que se autentique contra Responder; el hash/credencial permite montar el recurso SMB y subir un archivo Jamovi con ejecución.

```bash
curl -s 'http://<IP>/page.asp?cmd=whoami'
responder -I <IFACE> -wv
```

## Escalada de privilegios

La plantilla de certificados permite solicitar un certificado con EKU de smart card. Se añade el atributo, se pide el certificado y se configura PKINIT para obtener un TGT de Administrator.

```powershell
Certify.exe find /vulnerable
Certipy-ad req -u <USER> -p <PASS> -ca <CA> -template <TEMPLATE>
```

## Evidencia

- Ejecución ASP en el contenedor.
- Credenciales capturadas por Responder.
- Archivo Jamovi ejecutado en el host.
- Certificado emitido y TGT de Administrator.

## Lecciones aprendidas

- Un contenedor comprometido puede ser el punto de pivote.
- SSRF y Responder convierten una petición en credenciales.
- Los documentos de aplicaciones de análisis pueden ejecutar código.
- Una plantilla ADCS mal configurada puede dar Domain Admin.

## Mitigaciones y detección

- Validar entradas ASP y segregar contenedores.
- Bloquear salidas SMB/HTTP no necesarias y firmar SMB.
- Restringir plantillas ADCS y revisar EKU/permisos.
- Alertar de solicitudes de certificados y autenticaciones PKINIT anómalas.
- Referencias: CVE-2022-... ADCS, Certipy, HTB Anubis.

## Referencias

- <https://www.hackthebox.com/machines/Anubis>
- <https://posts.specterops.io/certified-pre-owned-d95910965cd2>
- <https://github.com/ly4k/Certipy>
- <https://attack.mitre.org/techniques/T1649/>
