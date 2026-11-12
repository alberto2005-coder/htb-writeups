---
topic: JuicyPotato
tags: [windows, privilege-escalation, seimpersonate, juicy-potato, com]
---

# JuicyPotato

**English** | [🇪🇸 Español](juicy-potato.md)

## Concept

JuicyPotato abuses `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` to run a process as SYSTEM. It coerces a COM server to authenticate against a controlled local RPC server and steals the resulting token.

## When it applies

- An account with `SeImpersonatePrivilege` (IIS, MSSQL, services).
- Windows before the 2019 mitigations or unpatched.
- A valid COM CLSID for the version/architecture.

## Requirements

1. `whoami /priv` showing the privilege enabled.
2. JuicyPotato binary and payload.
3. Compatible CLSID (per OS).
4. A free port for the local listener.

## Procedure

```powershell
whoami /priv
JuicyPotato.exe -l 1337 -p cmd.exe -a "/c whoami > C:\\temp\\out.txt" -t * -c {<CLSID>}
```

`-l` is the local port, `-p` the program, `-a` its arguments, `-t *` tries both token types and `-c` the CLSID. On success, the process runs as SYSTEM.

For a reverse shell:

```powershell
JuicyPotato.exe -l 1337 -p powershell.exe -a "-e <base64>" -t * -c {<CLSID>}
```

## Variants

- **RoguePotato**: for versions where JuicyPotato fails.
- **PrintSpoofer**: abuses spooler named pipes.
- **SweetPotato**: combines several vectors.
- **GodPotato**: supports more Windows versions.

## Limitations

- Microsoft fixed the vector on Windows 10 1809+/Server 2019 with COM changes.
- The CLSID must exist and be suitable.
- EDR may block coercion or token theft.
- It needs a privilege that is not always present.

## Mitigation

- Remove `SeImpersonatePrivilege` from service accounts where possible.
- Apply patches and COM mitigations.
- Run services under low-privilege accounts.
- Block unsigned binaries and monitor tokens.

## Detection

- Processes creating unusual local RPC servers.
- `SeImpersonatePrivilege` on web accounts.
- SYSTEM process creation from services.
- Potato/PrintSpoofer binaries on disk.

MITRE ATT&CK: T1134 (Access Token Manipulation), T1068 (Exploitation for Privilege Escalation).

## References

- <https://github.com/ohpe/juicy-potato>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/>
- <https://attack.mitre.org/techniques/T1134/>
