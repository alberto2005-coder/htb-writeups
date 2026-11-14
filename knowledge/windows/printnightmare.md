---
topic: PrintNightmare y el spooler de Windows
tags: [windows, printnightmare, spooler, cve-2021-34527, privilege-escalation]
---

# PrintNightmare y el spooler de Windows

[🇬🇧 English](printnightmare.en.md) | **Español**

## Concepto

PrintNightmare agrupa fallos del servicio Print Spooler que permiten cargar un driver o una DLL con privilegios. Las variantes RCE y LPE afectan a sistemas sin parchear y a configuraciones permisivas.

## Cuándo aplica

- `Spooler` activo en un servidor o estación.
- Credenciales de un usuario válido.
- Versiones de Windows anteriores a los parches de 2021.

## Procedimiento

1. Comprobar el servicio y los parches.
2. Enumerar si el usuario puede añadir drivers.
3. Preparar una DLL de driver.
4. Cargarla con una herramienta compatible.
5. Verificar la ejecución como SYSTEM.

```powershell
Get-Service Spooler
whoami /priv
```

## Variantes

- RCE remota contra el spooler.
- LPE con `AddPrinterDriver`.
- Abuso de `Point and Print` con un servidor controlado.

## Limitaciones

- El parche o la desactivación del spooler bloquean el ataque.
- Se necesitan credenciales o acceso local.
- EDR puede detectar la carga del driver.

## Mitigación

- Aplicar los parches de 2021.
- Deshabilitar el spooler si no se imprime.
- Restringir `Point and Print` y drivers.
- Auditar la instalación de drivers.

## Detección

- Creación de drivers inesperados.
- `spoolsv.exe` cargando DLLs de rutas de usuario.
- Eventos 808/316 del spooler.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2021-34527>
- <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34527>
- <https://attack.mitre.org/techniques/T1068/>
