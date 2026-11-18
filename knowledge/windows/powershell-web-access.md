---
topic: PowerShell Web Access — acceso remoto por navegador
tags: [windows, powershell, pswa, iis, lateral-movement, acute]
---

# PowerShell Web Access — acceso remoto por navegador

[🌐 English](powershell-web-access.en.md) | **Español**

## Concepto

PowerShell Web Access (PSWA) es una puerta de enlace de IIS que expone una consola PowerShell en el navegador. Permite administrar equipos sin RDP ni WinRM directo, y por eso aparece en redes donde solo se publica HTTPS. Para el atacante es una entrada completa: con credenciales válidas y un nombre de equipo se ejecutan comandos en el host de destino, y con `Invoke-Command` se salta a otros equipos y endpoints restringidos.

## Cuándo aplica

- IIS publica `/pswa` o un portal de administración que pide usuario, contraseña y equipo.
- Hay credenciales por defecto, reutilizadas o filtradas en documentos y metadatos.
- Los endpoints de PowerShell (`-ConfigurationName`) están configurados para delegar tareas.
- En Acute, el documento de bienvenida daba el formato de usuario y una contraseña inicial, y PSWA permitía entrar en `Acute-PC01`.

## Procedimiento

1. Descubrir el portal con fuzzing de directorios sobre HTTPS.
2. Obtener credenciales y una lista de usuarios y equipos.
3. Probar el login indicando el equipo de destino.
4. Enumerar la sesión: usuario, grupos, discos, procesos y red.
5. Usar `Invoke-Command` con los endpoints disponibles para saltar a otros hosts.
6. Cargar una herramienta de post-explotación si la consola es limitada.

## Comandos

```bash
feroxbuster -u https://<IP> -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

```text
https://<IP>/pswa
usuario: <DOMINIO>\<USUARIO>
equipo: <HOST>
```

```powershell
whoami /all
Get-ChildItem Env:
Get-Command -Module Microsoft.PowerShell.*
Invoke-Command -ComputerName <HOST> -ConfigurationName <ENDPOINT> -ScriptBlock { whoami; hostname } -Credential $cred
```

```powershell
$pass = ConvertTo-SecureString '<PASSWORD>' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('<DOMINIO>\<USUARIO>', $pass)
```

## Variantes

- Si PSWA exige un equipo concreto, probar los nombres del dominio y los hosts de administración.
- Con sesión limitada, usar `powershell.exe -EncodedCommand` para evitar restricciones de la consola.
- Si el portal está detrás de un proxy, reenviar con `curl` y mantener la cookie de sesión.
- Combinar con credenciales de documentos, correos o archivos de configuración.

## Limitaciones

- Requiere credenciales válidas y un equipo autorizado.
- Puede exigir MFA o restricciones por IP.
- La consola puede estar en modo restringido y sin acceso a disco.
- Los registros de IIS y de PowerShell recogen la actividad.

## Mitigación

- Deshabilitar PSWA si no es imprescindible; si se usa, exigir MFA y limitar por red.
- No publicar documentos con credenciales ni metadatos internos.
- Aplicar mínimo privilegio a los endpoints de `Invoke-Command`.
- Rotar contraseñas iniciales y prohibir su reutilización.
- Separar la administración en una red de gestión.

## Detección

- Peticiones a `/pswa` desde redes no administrativas.
- Logins correctos seguidos de `Invoke-Command` a varios hosts.
- Creación de procesos `wsmprovhost.exe` y `powershell.exe` en el destino.
- Uso de credenciales de una cuenta desde equipos no habituales.

## Referencias

- [Microsoft — PowerShell Web Access](https://learn.microsoft.com/en-us/powershell/scripting/learn/remoting/pswa)
- [Microsoft — about_Remote_FAQ](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_remote_faq)
- [0xdf — Acute](https://0xdf.gitlab.io/2022/07/16/htb-acute.html)
- [Ficha Acute](../../machines/windows/acute/README.md)
