---
topic: Excel XLL — malicious add-in execution
tags: [windows, phishing, xll, office, initial-access]
---

# Excel XLL — malicious add-in execution

**English** | [🌐 Español](xll-phishing.md)

## Concept

An XLL is a DLL that Excel loads as an add-in. It looks like an Excel file but is a PE that runs native code when enabled; an exported `xlAutoOpen` function is called automatically. It became a popular phishing vector as VBA macros were blocked.

## When it applies

- The organization uses Excel and allows add-ins from untrusted locations.
- Email or a share delivers `.xll` files.
- The goal is desktop execution without relying on VBA macros.

## Procedure

1. Create a DLL project with the Excel SDK and export `xlAutoOpen`.
2. Build in Release to avoid debug dependencies.
3. Implement a reverse shell or loader and send the XLL by email or chat.
4. Wait for the user to enable the add-in and catch the connection.

## Commands

```bash
dumpbin /exports payload.xll
swaks --to user@domain --from support@domain --attach payload.xll --body "Open the attached add-in"
# The relevant export must appear as xlAutoOpen
```

## Variants

- Sign the XLL with a stolen or lab certificate.
- Place the `.xll` inside a ZIP to bypass extension filters.
- Change the icon and name so it looks like a spreadsheet.

## Limitations

- Microsoft blocks untrusted XLLs by default since 2023.
- Mark-of-the-Web and SmartScreen reduce execution.
- The XLL architecture must match Excel.

## Mitigation

- Block XLLs from the Internet and untrusted locations.
- Apply ASR, WDAC/AppLocker and Mark-of-the-Web.
- Raise awareness of add-ins and disguised executables.

## Detection

- Excel loading a DLL from `Downloads`, `Temp` or a share.
- Child process creation events under `EXCEL.EXE`.
- Email with `.xll`, `.xla` attachments or ZIPs containing them.

## References

- [0xdf — Axlle](https://0xdf.gitlab.io/2024/11/16/htb-axlle.html)
- [Microsoft — XLL add-ins](https://learn.microsoft.com/en-us/office/client-developer/excel/xll-add-ins)
- [MITRE T1204.002 — Malicious File](https://attack.mitre.org/techniques/T1204/002/)
