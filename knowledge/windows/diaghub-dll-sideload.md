---
topic: DiagHub — carga de DLL como SYSTEM
tags: [windows, diaghub, dll, arbitrariowrite, system, privesc, hackback]
---

# DiagHub — carga de DLL como SYSTEM

[🌐 English](diaghub-dll-sideload.en.md) | **Español**

## Concepto

DiagHub es el servicio Microsoft Diagnostics Hub Standard Collector, que se ejecuta como SYSTEM y se invoca a través de COM. Al instanciar su objeto, el servicio carga una biblioteca desde `C:\Windows\System32`. Si un atacante consigue escribir en ese directorio, puede colocar una DLL con el nombre esperado y hacer que el servicio la cargue con privilegios de SYSTEM. En Hackback, un servicio que escribía logs como SYSTEM permitía colocar el archivo y DiagHub completaba la escalada.

## Cuándo aplica

- El servicio `DiagnosticsHub.StandardCollector.Service` está presente y activo.
- Se dispone de escritura arbitraria como SYSTEM o como administrador en `System32`.
- El servicio carga DLLs desde una ruta fija y sin validar la firma.
- Hay un mecanismo previo que permite escribir el archivo (un servicio con log redirigible, una tarea, un instalador).

## Procedimiento

1. Enumerar el servicio y su configuración.
2. Confirmar que se puede invocar por COM sin privilegios.
3. Conseguir escritura en `System32` (en Hackback, redirigiendo el log de `UserLogger`).
4. Compilar una DLL que ejecute un comando al cargarse.
5. Colocarla con el nombre que espera el servicio.
6. Invocar el objeto COM y comprobar la ejecución como SYSTEM.

## Comandos

```powershell
sc qc DiagnosticsHub.StandardCollector.Service
sc query DiagnosticsHub.StandardCollector.Service
reg query "HKLM\SYSTEM\CurrentControlSet\Services\DiagnosticsHub.StandardCollector.Service"
```

```powershell
$type = [Type]::GetTypeFromCLSID('<CLSID>')
$obj = [Activator]::CreateInstance($type)
```

```c
// DLL mínima: ejecuta un comando en DllMain
BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID r) {
    if (reason == DLL_PROCESS_ATTACH) system("cmd.exe /c <COMANDO>");
    return TRUE;
}
```

## Variantes

- Usar `rundll32` o un servicio propio para forzar la carga si COM falla.
- Si no hay escritura en `System32`, buscar una ruta de carga configurable.
- Combinar con un servicio que escriba como SYSTEM para obtener el archivo.
- Usar una DLL firmada si el servicio valida la firma.

## Limitaciones

- Requiere escritura en un directorio protegido, que suele ser el paso difícil.
- La versión de Windows y del servicio puede cambiar la ruta o el nombre.
- Un EDR puede bloquear la carga de DLL sin firma.
- La DLL se ejecuta una sola vez por instancia; conviene que sea idempotente.

## Mitigación

- Restringir la escritura en `System32` y auditar las ACL de los servicios.
- Aplicar WDAC o AppLocker para DLLs sin firma.
- Revisar los servicios que escriben logs en rutas controlables.
- Actualizar Windows y monitorizar la creación de archivos en `System32`.
- Usar credenciales de servicio gestionadas y mínimo privilegio.

## Detección

- Creación de DLLs en `System32` fuera de una actualización.
- Arranque del servicio DiagHub seguido de procesos hijos.
- Eventos 7045 de instalación de servicios y cambios de `ImagePath`.
- Cargas de DLL sin firma desde procesos de SYSTEM.

## Referencias

- [Microsoft — Diagnostics Hub](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/)
- [MITRE ATT&CK — DLL Side-Loading](https://attack.mitre.org/techniques/T1574/002/)
- [0xdf — Hackback](https://0xdf.gitlab.io/2019/07/06/htb-hackback.html)
- [Ficha Hackback](../../machines/windows/hackback/README.md)
