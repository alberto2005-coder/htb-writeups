---
topic: Windows — poisoned LNK and MSI signed with a leaked CA
tags: [windows, lnk, msi, code-signing, ca, lateral-movement, privesc]
---

# Windows — poisoned LNK and MSI signed with a leaked CA

**English** | [🌐 Español](lnk-msi-lateral-movement.md)

## Concept

A writable shortcut executed by another user can be replaced with an LNK that launches a shell. If a code-signing CA private key is also leaked and an administrator runs MSIs from a watched directory, sign a malicious MSI and execute as that administrator.

## When it applies

- An LNK in a public path is writable.
- Another user opens it periodically or at logon.
- A private CA is accessible and an MSI deployment directory exists.

## Procedure

1. Analyze the LNK with `pylnker` or `LECmd`.
2. Generate an LNK with `LNKUp` that runs the payload.
3. Replace the file and wait for execution.
4. Sign an MSI with the leaked CA and drop it in the watched directory.

## Commands

```bash
python LNKUp/generate.py --host localhost --type ntlm --out evil.lnk --execute 'cmd /c ...'
makecert -pe -n "CN=My SPC" -cy end -sky signature -ic MyCA.cer -iv MyCA.pvk -sv MySPC.pvk MySPC.cer
pvk2pfx -pvk MySPC.pvk -spc MySPC.cer -pfx MySPC.pfx
signtool sign /f MySPC.pfx /fd sha256 payload.msi
```

## Variants

- LNK with `powershell`, `mshta` or double OpenSSL.
- MSI with a custom action.
- Scheduled task running the MSI.

## Limitations

- The script may replace the LNK after execution.
- The user may lack write access.
- The CA may not be in the trusted store.

## Mitigation

- Restrict writes to public shortcuts.
- Protect and rotate the CA private key.
- Verify MSI origin and signature.
- Audit deployment directories.

## Detection

- Changes to LNKs in public paths.
- New MSIs in watched directories.
- `msiexec` running binaries outside the catalog.

## References

- [0xdf — Ethereal](https://0xdf.gitlab.io/2019/03/09/htb-ethereal.html)
- [Microsoft — signtool](https://learn.microsoft.com/en-us/windows/win32/seccrypto/signtool)
- [MITRE — T1204.002](https://attack.mitre.org/techniques/T1204/002/)
