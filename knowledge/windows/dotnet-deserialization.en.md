---
topic: Deserialización .NET
tags: [windows, dotnet, deserialization, ysoserial, rce]
---

# Deserialización .NET

**English** | [🇪🇸 Español](dotnet-deserialization.md)

## Concept

A .NET application deserializes user-controlled data with formatters such as `BinaryFormatter`, `ObjectStateFormatter` or `LosFormatter`. Gadget chains execute code during deserialization.

## When it applies

- ViewState, cookies, caches or forms serializing .NET objects.
- Applications accepting a base64 blob and calling `Deserialize`.
- Legacy components with `TypeConfuseDelegate` or other gadgets.

## Procedure

1. Identify the formatter and the serialized field.
2. Generate the payload with YSoSerial.NET.
3. Encode it as the application expects (base64, URL, ViewState).
4. Send it and confirm execution with a callback.

```bash
ysoserial.exe -g TypeConfuseDelegate -f ObjectStateFormatter -o payload.txt
ysoserial.exe -g TypeConfuseDelegate -f BinaryFormatter -c "cmd /c whoami" -o payload.bin
# Encode for the field and send with curl or Burp
```

## Variants

- `LosFormatter` in unsigned ViewState.
- `BinaryFormatter` in WCF/Remoting services.
- Third-party gadgets (Json.NET, SharpZipLib).
- In-memory deserialization from a queue or cache.

## Limitations

- The formatter must accept the gadget and the version must match.
- ViewState may be signed and encrypted.
- Execution depends on the loaded assemblies.

## Mitigation and detection

- Avoid `BinaryFormatter` and unsafe formatters; use JSON with explicit types.
- Sign and encrypt ViewState, and validate the MAC.
- Monitor child processes of `w3wp.exe` and anomalous outbound traffic.

## References

- <https://github.com/pwntester/ysoserial.net>
- <https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide>
- <https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html>
