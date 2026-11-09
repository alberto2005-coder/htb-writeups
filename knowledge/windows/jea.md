---
title: JEA — ejecutar comandos en un endpoint restringido y sacarle partido
tags: [windows, powershell, jea, winrm, privesc]
---

# JEA: endpoints restringidos, `& { }` y el historial de PSReadLine

[🇬🇧 English](jea.en.md) | **Español**

## 1. Qué es JEA

*Just Enough Administration* publica un endpoint de PowerShell Remoting (WinRM) que ejecuta como una cuenta privilegiada, pero solo permite los comandos y parámetros declarados en su *role capability*. El cliente ve un espacio de nombres limitado y no puede llamar a cmdlets arbitrarios.

Desde fuera es un `PSSessionConfiguration` más:

```powershell
Get-PSSessionConfiguration
Get-PSSessionConfiguration -Name '<CONFIG>' | Format-List *
```

## 2. Conectarse desde Linux

`pypsrp` habla WSMan sin necesidad de Windows:

```python
from pypsrp.client import Client

c = Client('<HOST>', username='<domain>\\<user>', password='<password>', ssl=False)
out, streams, errs = c.execute_ps('Get-Command | Select-Object -ExpandProperty Name')
print(out)
```

Si el endpoint solo acepta Kerberos, `pypsrp` acepta `negotiate` con el `ccache` (`KRB5CCNAME`).

## 3. El wrapper `& { }`

La sesión restringida evalúa el scriptblock con un parser limitado: no hay funciones propias, ni clases, ni variables fuera de las automáticas. Pero `&` con un scriptblock literal es una construcción permitida, así que agrupar varias sentencias aprobadas dentro de `& { ... }` evita que el parser rechace la secuencia:

```python
ps = r'''
& {
  $x = Get-ChildItem 'C:\ProgramData\<carpeta>'
  $x | ForEach-Object { $_.FullName }
}
'''
c.execute_ps(ps)
```

Lo importante: **solo se ejecutan cmdlets aprobados**. El wrapper no salta la lista blanca; sirve para componer varias llamadas y para que la salida no se pierda entre sentencias.

## 4. Lo que suele estar permitido y da juego

- `Get-ChildItem`, `Get-Content`, `Get-Item` sobre rutas concretas.
- `Get-Service`, `Get-Process`, `Get-CimInstance` de clases permitidas.
- Scripts propios publicados en el `RoleCapabilities` (a veces con parámetros sin validar).

Revisa el `.psrc` del endpoint (`C:\Program Files\WindowsPowerShell\Modules\...\RoleCapabilities\*.psrc` o el `SessionConfiguration` en el registro) para ver la lista real.

## 5. Historial de PSReadLine

Cada usuario guarda sus comandos en:

```text
C:\Users\<usuario>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

Si el endpoint corre como una cuenta con acceso a ese perfil (o si puedes leerlo con los cmdlets permitidos), el historial suele contener **credenciales en línea de comandos**: `net use`, `Invoke-Sqlcmd -Password`, `sshpass`, `runas`. Es una de las formas más rápidas de escalar de «puedo ejecutar cuatro cmdlets» a «tengo la cuenta del administrador del endpoint».

```python
c.execute_ps(r"Get-Content 'C:\Users\<usuario>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt'")
```

## 6. Errores típicos

- **`The term 'X' is not recognized`** → cmdlet fuera de la role capability; no hay bypass, hay que buscar otro permitido.
- **`Access is denied` con `pypsrp`** → el endpoint exige Kerberos o un grupo concreto; usa `-k` con `ccache`.
- **`Connecting to remote server failed`** → WinRM en 5985/5986 cerrado o el `ConfigurationName` no existe.
- **Salida vacía** → el scriptblock no devuelve objetos; envuelve en `Write-Output` si está permitido o usa `Out-String`.

## 7. Detección y mitigación

- **4104** (script block logging) muestra el scriptblock enviado, incluido el wrapper `& { }`.
- **4688** con `powershell.exe` como hijo de `wsmprovhost.exe`.
- Transcripciones de JEA (`TranscriptDirectory`) y logs de WinRM.
- Auditar las role capabilities: mínimo privilegio, parámetros validados, sin `Get-Content` sobre perfiles ajenos.
- Restringir quién puede conectarse al endpoint y con qué cuenta corre.

MITRE: T1059.001, T1552.001, T1078.
