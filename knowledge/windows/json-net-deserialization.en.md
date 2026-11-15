---
topic: Json.Net — Bearer deserialization with TypeNameHandling
tags: [windows, dotnet, json.net, deserialization, ysoserial]
---

# Json.Net — Bearer deserialization with TypeNameHandling

[🇪🇸 Español](json-net-deserialization.md) | **English**

## Concept

Newtonsoft.Json can embed the .NET type in JSON through `$type` when `TypeNameHandling` is not `None`. If an endpoint deserializes the Bearer token or a cookie with that setting, an object carrying a `ysoserial.net` gadget runs code during construction.

## When it applies

- The application uses Json.Net for tokens, cookies or API bodies.
- `TypeNameHandling` is `All`, `Objects` or `Auto`.
- The assembly with the gadget is available on the server.

## Procedure

1. Decode the token and check whether it accepts JSON with `$type`.
2. Generate a payload with the `WindowsIdentity` gadget and `Json.Net` formatter.
3. Send it in the Bearer, cookie or deserialized field.
4. Observe execution and start a reverse shell.

```bash
ysoserial.exe -g WindowsIdentity -f Json.Net -c "whoami" -o base64
```

```text
Authorization: Bearer <BASE64>
```

## Variants

- `ObjectDataProvider` gadget with `Json.Net`.
- `TypeNameHandling=Auto` in a nested field.
- `JsonConvert.DeserializeObject` on the full request body.

## Limitations

- `TypeNameHandling=None` blocks the attack.
- The gadget must exist and be loadable.
- A WAF may block `$type` or base64 with known signatures.

## Mitigation

- Use `TypeNameHandling.None` and concrete DTOs.
- Validate the token on a server that does not deserialize arbitrary types.
- Sign and encrypt the token; do not trust its content.

## Detection

- Requests with `$type` or base64 decoding to JSON containing `$type`.
- Child processes of `w3wp.exe` or the .NET service.
- Deserialization errors containing assembly names.

## References

- [0xdf — Json](https://0xdf.gitlab.io/2020/02/15/htb-json.html)
- [ysoserial.net — Json.Net formatter](https://github.com/pwntester/ysoserial.net)
- [Newtonsoft — TypeNameHandling](https://www.newtonsoft.com/json/help/html/T_Newtonsoft_Json_TypeNameHandling.htm)
