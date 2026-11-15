---
topic: Deserialización .NET
tags: [windows, dotnet, deserialization, ysoserial, rce]
---

# Deserialización .NET

[🌐 English](dotnet-deserialization.en.md) | **Español**

## Concepto

Una aplicación .NET deserializa datos controlados por el usuario con formateadores como `BinaryFormatter`, `ObjectStateFormatter` o `LosFormatter`. Los gadgets de la cadena permiten ejecutar código durante la deserialización.

## Cuándo aplica

- ViewState, cookies, cachés o formularios que serializan objetos .NET.
- Aplicaciones que aceptan un blob base64 y llaman a `Deserialize`.
- Componentes antiguos con `TypeConfuseDelegate` u otros gadgets.

## Procedimiento

1. Identificar el formateador y el campo serializado.
2. Generar el payload con YSoSerial.NET.
3. Codificarlo como espera la aplicación (base64, URL, ViewState).
4. Enviarlo y comprobar la ejecución con un callback.

```bash
ysoserial.exe -g TypeConfuseDelegate -f ObjectStateFormatter -o payload.txt
ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c "cmd /c whoami" -o payload.bin
# Codificar según el campo y enviar con curl o Burp
```

## Variantes

- `LosFormatter` en ViewState sin MAC.
- `BinaryFormatter` en servicios WCF/Remoting.
- Gadgets de terceros (Json.NET, SharpZipLib).
- Deserialización en memoria desde una cola o caché.

## Limitaciones

- El formateador debe aceptar el gadget y la versión debe ser compatible.
- ViewState puede estar firmado y cifrado.
- La ejecución depende de los ensamblados cargados.

## Mitigación y detección

- Evitar `BinaryFormatter` y formateadores inseguros; usar JSON con tipos explícitos.
- Firmar y cifrar ViewState, y validar el MAC.
- Monitorizar procesos hijos de `w3wp.exe` y tráfico saliente anómalo.

## Referencias

- <https://github.com/pwntester/ysoserial.net>
- <https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide>
- <https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html>
