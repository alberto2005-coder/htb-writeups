---
topic: PsExec
tags: [windows, psexec, smb, lateral-movement, service, impacket]
---

# PsExec

[🌐 English](psexec.en.md) | **Español**

## Concepto

PsExec ejecuta un comando en un equipo remoto creando temporalmente un servicio y un binario en el recurso administrativo `ADMIN$`. Requiere credenciales con privilegios administrativos y conectividad SMB; deja rastros claros en el servicio, el registro y el sistema de archivos.

## Cuándo aplica

- Credenciales de administrador local o de dominio.
- SMB y `ADMIN$` accesibles.
- Movimiento lateral entre servidores Windows.
- Uso de hash NTLM en lugar de contraseña.

## Procedimiento

1. Confirmar SMB y permisos administrativos.
2. Validar credenciales con `netexec` o `smbclient`.
3. Ejecutar el comando remoto.
4. Revisar la salida y el estado del servicio.
5. Documentar el artefacto creado.

```bash
nxc smb <HOST> -u <USER> -p '<PASSWORD>' --shares
impacket-psexec <DOMAIN>/<USER>:'<PASSWORD>'@<HOST> 'whoami'
impacket-psexec -hashes :<NTLM> <DOMAIN>/<USER>@<HOST>
```

## Variantes

- `PsExec.exe` oficial o `impacket-psexec`.
- `smbexec` y `wmiexec` como alternativas.
- Pass-the-Hash con NTLM.
- Servicio temporal con binario en `ADMIN$`.

## Limitaciones

- Se necesitan privilegios administrativos.
- SMB puede estar filtrado por firewall.
- EDR puede bloquear la creación del servicio.
- El binario puede eliminarse al terminar.

## Mitigación y detección

- Restringir SMB y cuentas administrativas locales.
- Aplicar LAPS y segmentación.
- Monitorizar eventos 7045, 4688 y creación de servicios.
- Alertar de `PSEXESVC`, `ADMIN$` y ejecución remota.

## Referencias

- <https://learn.microsoft.com/en-us/sysinternals/downloads/psexec>
- <https://attack.mitre.org/techniques/T1021/002/>
- <https://github.com/fortra/impacket>
