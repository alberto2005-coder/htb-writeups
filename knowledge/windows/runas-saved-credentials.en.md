---
topic: runas saved credentials
tags: [windows, privilege-escalation, runas, credentials, dpapi]
---

# runas saved credentials

**English** | [🇪🇸 Español](runas-saved-credentials.md)

## Concept

`runas /savecred` stores credentials in the user profile for reuse without retyping the password. If an administrator saved them in an accessible session, a low-privilege user can run processes as that account.

## When it applies

- Windows where `runas /savecred` was used before.
- Accessible user profile with stored credentials.
- Saved account with high privileges.

## Requirements

1. Shell on the host as a low-privilege user.
2. Credentials stored in the current or accessible profile.
3. `runas.exe` available.

## Procedure

```powershell
runas /user:<DOMAIN>\\<USER> /savecred "cmd.exe /c whoami"
```

If the credential is saved, the command runs without a prompt. For a reverse shell:

```powershell
runas /savecred /user:Administrator "powershell -e <base64>"
```

Credentials are stored in the profile's Credential Manager/DPAPI. Enumerate with:

```powershell
cmdkey /list
```

## Variants

- **Credential Manager**: `Domain:interactive` entries.
- **DPAPI**: blobs under `%APPDATA%\\Microsoft\\Credentials`.
- **Privileged programs**: binaries calling `runas /savecred`.
- **Scheduled tasks**: store credentials for execution.

## Limitations

- Only works if the credential was saved and is valid.
- The user must be able to start the process.
- UAC may block elevation.
- EDR may alert on `runas` with `/savecred`.

## Mitigation

- Avoid `runas /savecred` on privileged accounts.
- Clear Credential Manager and DPAPI.
- Use managed service accounts.
- Restrict profile access and audit `cmdkey`.

## Detection

- `runas.exe` execution with `/savecred`.
- `cmdkey /list` from non-admin accounts.
- Child processes of `runas` with high privileges.
- Unusual DPAPI blob access.

MITRE ATT&CK: T1555 (Credentials from Password Stores), T1078 (Valid Accounts).

## References

- <https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/runas>
- <https://attack.mitre.org/techniques/T1555/>
- <https://attack.mitre.org/techniques/T1078/>
