---
topic: ThemeBleed CVE-2023-38146
tags: [windows, themebleed, cve-2023-38146, msstyles, dll]
---

# ThemeBleed CVE-2023-38146

[🌐 Español](themebleed.md) | **English**

## Concept

ThemeBleed is a Windows 11 theme loader vulnerability. A crafted `.msstyles` file makes the system resolve a UNC path and load an attacker-controlled DLL when the theme is previewed.

## When it applies

- Windows 11 without the September 2023 patch.
- The user opens or previews a `.theme`/`.msstyles` file.
- The attacker can host a DLL on a reachable UNC resource.

## Procedure

1. Create a theme whose `.msstyles` points to a UNC resource.
2. Host a DLL that runs when loaded.
3. Deliver the theme and wait for preview.
4. Confirm execution in the user's context.

```powershell
# Build the .msstyles and DLL, host them at \<HOST>\share
# Open the .theme on the target
```

## Variants

- DLL with a reverse shell or loader.
- UNC path with credentials to capture NetNTLM.
- Chain with a later privilege escalation flaw.

## Limitations

- The target must preview the theme.
- The UNC path must be reachable.
- The Windows patch blocks loading.

## Mitigation

- Update Windows.
- Block untrusted themes and outbound UNC.
- Disable automatic preview.

## Detection

- `.msstyles`/`.theme` creation in downloads.
- Outbound SMB to unusual hosts.
- `explorer.exe` loading DLLs from network paths.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2023-38146>
- <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-38146>
- <https://attack.mitre.org/techniques/T1222/>
