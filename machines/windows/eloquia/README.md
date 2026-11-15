---
machine: Eloquia
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, angularjs, csti, oauth, sqlite, dpapi, appdomainmanager, privesc]
---

# Eloquia — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un CSTI de AngularJS en los artículos permite ejecutar directivas y saltar la CSP; se roba la cookie del bot admin o se vincula su cuenta OAuth. Como admin se sube una extensión SQLite maliciosa y se carga desde SQL Explorer para obtener una shell como `web`. Las contraseñas guardadas de Edge se descifran con DPAPI y dan `olivia.kat`; un `.exe.config` escribible permite un AppDomainManager malicioso y Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,5985 <IP>
```

- `80` IIS con `eloquia.htb` y `5985` WinRM.
- La web es Django con artículos, comentarios y login OAuth contra un clon de Google (`qooqle.htb`).
- `feroxbuster` enumera `/admin`, `/accounts` y `/articles`.

## Enumeración

- El cuerpo de los artículos se renderiza con AngularJS y permite CSTI.
- La CSP bloquea scripts inline, pero las directivas `ng-*` ejecutan expresiones.
- Se puede robar la cookie del bot administrador o encadenar un CSRF/OAuth para vincular la cuenta admin a una controlada.

## Foothold

Como admin se accede a Django Admin y se sube una extensión SQLite `.so` maliciosa. SQL Explorer permite cargarla y ejecutar una función, lo que da una shell como `web`.

```text
SELECT load_extension('/uploads/evil.so');
```

## Movimiento lateral

En el perfil de Edge hay contraseñas guardadas. Se extraen con `dpapi`/PowerShell y se descifran con la clave del usuario; una de ellas funciona para `olivia.kat` por WinRM.

```powershell
.\dpapi.py credential -file <CRED> -key <KEY>
```

## Escalada de privilegios

`olivia.kat` puede escribir en `C:\Program Files\Qooqle IPS Software\Failure2Ban - Prototype\Failure2Ban\bin\Debug`. El servicio se reinicia periódicamente y lee `Failure2Ban.exe.config`. Se añade `<appDomainManagerAssembly>` y `<appDomainManagerType>` apuntando a una DLL gestionada que cambia la contraseña de Administrator al arrancar.

```xml
<appDomainManagerAssembly value="admin, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null" />
<appDomainManagerType value="oxdfDomainManager.oxdfManager" />
```

## Evidencia

- CSTI AngularJS y bypass de CSP.
- Robo de cookie/OAuth del admin.
- Extensión SQLite y shell como `web`.
- DPAPI de Edge y `olivia.kat`.
- `Failure2Ban.exe.config` y Administrator.

## Lecciones aprendidas

- AngularJS sin sanitizar es ejecución de expresiones en el cliente.
- La CSP no protege si se permiten directivas peligrosas.
- Las extensiones SQLite son código nativo.
- Los secretos de Edge se descifran con DPAPI del usuario.
- Un `.config` escribible permite cargar una DLL gestionada en un servicio.

## Mitigación y detección

- Escapar HTML y usar `ng-csp`/CSP estricta.
- Validar OAuth `state` y `redirect_uri`.
- No permitir `load_extension` en SQLite.
- Proteger perfiles de navegador y credenciales.
- Restringir permisos de servicio y firmar assemblies.

## Referencias

- [0xdf — Eloquia](https://0xdf.gitlab.io/2026/10/17/htb-eloquia.html)
- [IppSec — Eloquia](https://www.youtube.com/watch?v=aRSUIJXxbDc)
- [Hack The Box — Eloquia](https://app.hackthebox.com/machines/eloquia)
