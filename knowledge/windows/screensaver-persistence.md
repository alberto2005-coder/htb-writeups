---
topic: Persistencia mediante screensaver
tags: [windows, persistence, screensaver, scr, registry, run-key]
---

# Persistencia mediante screensaver

[🌐 English](screensaver-persistence.en.md) | **Español**

## Concept

Windows ejecuta el screensaver configurado cuando el equipo queda inactivo. Si un atacante coloca un `.scr` malicioso y cambia la configuración del screensaver o una entrada `Run`, el programa se ejecuta al bloquearse la sesión o al iniciar sesión.

## Cuándo aplica

- Claves `HKCU\Control Panel\Desktop` con `SCRNSAVE.EXE`.
- Entradas `Run` que apuntan a un `.scr` en `AppData`.
- Archivos `.scr` sin firma en rutas de usuario.
- Equipos con políticas de screensaver permisivas.

## Procedimiento

1. Revisar la configuración del screensaver en el registro.
2. Localizar el archivo `.scr` y comprobar su firma.
3. Revisar entradas `Run`, `RunOnce` y tareas programadas.
4. Analizar el binario y su C2.
5. Correlacionar con la hora de inicio de sesión o bloqueo.

```powershell
Get-ItemProperty 'HKCU:\Control Panel\Desktop' -Name SCRNSAVE.EXE
Get-ChildItem "$env:APPDATA" -Recurse -Filter *.scr
```

## Variantes

- `SCRNSAVE.EXE` apuntando a `AppData`.
- Entrada `Run` con un `.scr`.
- Política de screensaver que ejecuta un binario del usuario.
- Sustitución de un screensaver legítimo.
- Ejecución al bloquear la sesión.

## Limitaciones

- El screensaver debe estar habilitado.
- La ruta debe ser accesible por el usuario.
- Algunos EDR bloquean `.scr` desde `AppData`.
- La ejecución depende de la inactividad o del bloqueo.

## Mitigación y detección

- Restringir screensavers a rutas de sistema firmadas.
- Monitorizar cambios en `Control Panel\Desktop` y entradas `Run`.
- Bloquear ejecución de `.scr` desde perfiles de usuario.
- Alertar de procesos `.scr` con conexiones de red.

## Referencias

- <https://attack.mitre.org/techniques/T1546/002/>
- <https://attack.mitre.org/techniques/T1547/001/>
- <https://learn.microsoft.com/en-us/windows/win32/controls/about-screen-savers>
- <https://www.microsoft.com/en-us/security/blog/>
