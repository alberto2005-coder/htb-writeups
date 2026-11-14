---
topic: Windows IoT Core y Sirep
tags: [windows, iot, sirep, wdp, registry, credentials, omni]
---

# Windows IoT Core y Sirep

[🌐 English](iot-core-sirep.en.md) | **Español**

## Concept

Windows IoT Core expone el protocolo Sirep en el puerto 29826 y Windows Device Portal (WDP) en el 8080. Sirep permite ejecutar comandos y transferir archivos; si no está restringido, un atacante puede guardar colmenas del registro, extraer credenciales y ejecutar código como administrador.

## Cuándo aplica

- Dispositivos IoT con Windows IoT Core.
- Puertos 29826 y 8080 accesibles.
- Credenciales de administrador por defecto o débiles.
- Entornos de laboratorio que replican Omni.

## Procedimiento

1. Enumerar puertos y confirmar Sirep/WDP.
2. Usar SirepRAT para ejecutar comandos.
3. Guardar `SAM` y `SYSTEM` con `reg save`.
4. Extraer hashes con `secretsdump`.
5. Acceder a WDP y ejecutar PowerShell como administrador.

```bash
python3 SirepRAT.py <IP> GetSystemInformationFromDevice
python3 SirepRAT.py <IP> ExecuteCommandWithOutput --return_output --cmd "cmd.exe /c whoami"
```

## Variantes

- `reg save HKLM\SAM` y `HKLM\SYSTEM` para volcado offline.
- `Import-Clixml` de credenciales guardadas.
- WDP con credenciales por defecto.
- Ejecución de PowerShell a través de la API de administración.

## Limitaciones

- Sirep debe estar habilitado y accesible.
- WDP puede requerir autenticación.
- Las credenciales extraídas pueden estar rotadas.
- La versión de IoT Core limita los comandos disponibles.

## Mitigación y detección

- Deshabilitar Sirep y WDP fuera del laboratorio.
- Segmentar dispositivos IoT y cambiar credenciales.
- Restringir los puertos 29826 y 8080 por firewall.
- Alertar de `reg save`, accesos a WDP y comandos remotos.

## Referencias

- <https://github.com/SafeBreach-Labs/SirepRAT>
- <https://learn.microsoft.com/en-us/windows/iot/iot-enterprise/develop/device-portal>
- <https://attack.mitre.org/techniques/T1003/002/>
- <https://attack.mitre.org/techniques/T1210/>
