---
machine: SolarLab
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, reportlab, cve-2023-33733, openfire, runascs, privesc]
---

# SolarLab — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un recurso SMB expone documentos y un Excel con usuarios y contraseñas. La aplicación ReportHub genera PDFs con ReportLab 3.6.12 y pasa los campos del formulario a la plantilla. CVE-2023-33733 escapa del sandbox y da una shell como `blake`. El código y `users.db` revelan credenciales de `openfire`; con RunasCs se obtiene esa cuenta, y la clave de cifrado de OpenFire permite descifrar la contraseña de Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,135,139,445,6791,7680 <IP>
```

- `80` y `6791` redirigen a ReportHub; `135` RPC, `139`/`445` SMB y `7680` un servicio desconocido.
- RDP (3389) y WinRM (5985/5986) no están expuestos.
- El recurso `Documents` es accesible como `guest`.
- ReportHub permite crear solicitudes de ausencia, formación y viajes, y exporta un PDF.

## Enumeración

En `Documents` hay un Excel con usuarios y contraseñas. Un RID brute y `ffuf` permiten enumerar nombres de usuario; el spray con las contraseñas de la hoja acierta la de `blake`, que accede a ReportHub en `6791`. El código de la aplicación vive en `C:\Users\blake\Documents\app` y usa ReportLab para generar el PDF.

## Foothold

La aplicación pasa los campos del formulario, como `phone` o `destination`, a la generación del PDF. ReportLab 3.6.12 es vulnerable a CVE-2023-33733: una etiqueta `<font color="...">` con una expresión construida con `getattr` y `__globals__` ejecuta código al renderizar. El servidor devuelve un 500, pero el comando se ejecuta.

```text
<font color="[[getattr(pow,W('__globals__'))['os'].system('ping <IP>')for W in [o('W',(str,),{...})]] for o in [type(type(1))]]">e</font>
```

## Movimiento lateral

Como `blake` se leen `app.py`, `routes.py` y `instance/users.db`. La base SQLite contiene contraseñas en claro; una de ellas pertenece a `openfire`. `RunasCs.exe` permite iniciar sesión con esas credenciales y obtener una shell como `openfire`.

## Escalada de privilegios

OpenFire está instalado en `C:\Program Files\Openfire`. Su configuración guarda la contraseña de Administrator cifrada con Blowfish/CBC y una clave en `openfire.xml`. Con un script que reproduce el descifrado se obtiene la contraseña de Administrator; `psexec.py` sobre SMB da SYSTEM.

```bash
psexec.py solarlab.htb/administrator:'<password>'@solarlab.htb powershell
```

La vía alternativa es CVE-2023-32315 en OpenFire 4.7.4: el traversal con `%u002e%u002e` permite crear un administrador y subir un plugin con RCE.

## Evidencia

- Excel compartido con usuarios y contraseñas.
- Petición a ReportHub con la etiqueta `<font color>`.
- `users.db` con usuarios y contraseñas.
- Contraseña de Administrator descifrada y `psexec.py`.

## Lecciones aprendidas

- Los documentos compartidos por SMB contienen secretos de aplicación.
- ReportLab evalúa expresiones en el color de una fuente.
- Las contraseñas en claro en SQLite amplían el movimiento lateral.
- Las claves de cifrado junto a los datos cifrados anulan la protección.

## Mitigación y detección

- Actualizar ReportLab a 3.6.13 o superior y no evaluar HTML del usuario.
- Restringir el recurso SMB y proteger los documentos con contraseñas fuertes.
- Hashear las contraseñas de la aplicación y separar la clave de cifrado.
- Auditar la creación de usuarios y plugins en OpenFire.

## Referencias

- [0xdf — SolarLab](https://0xdf.gitlab.io/2024/09/21/htb-solarlab.html)
- [IppSec — SolarLab](https://www.youtube.com/watch?v=BGp_Y3tbLP0)
- [Hack The Box — SolarLab](https://app.hackthebox.com/machines/solarlab)
