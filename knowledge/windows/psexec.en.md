---
topic: PsExec
tags: [windows, psexec, smb, lateral-movement, service, impacket]
---

# PsExec

**English** | [🇪🇸 Español](psexec.md)

## Concept

PsExec runs a command on a remote computer by temporarily creating a service and a binary in the `ADMIN$` administrative share. It requires credentials with administrative privileges and SMB connectivity; it leaves clear traces in the service, registry and file system.

## When it applies

- Local administrator or domain credentials.
- SMB and `ADMIN$` reachable.
- Lateral movement between Windows servers.
- Using an NTLM hash instead of a password.

## Procedure

1. Confirm SMB and administrative permissions.
2. Validate credentials with `netexec` or `smbclient`.
3. Run the remote command.
4. Check output and service state.
5. Document the created artefact.

```bash
nxc smb <HOST> -u <USER> -p '<PASSWORD>' --shares
impacket-psexec <DOMAIN>/<USER>:'<PASSWORD>'@<HOST> 'whoami'
impacket-psexec -hashes :<NTLM> <DOMAIN>/<USER>@<HOST>
```

## Variants

- Official `PsExec.exe` or `impacket-psexec`.
- `smbexec` and `wmiexec` as alternatives.
- Pass-the-Hash with NTLM.
- A temporary service with a binary in `ADMIN$`.

## Limitations

- Administrative privileges are required.
- SMB may be filtered by a firewall.
- EDR may block service creation.
- The binary may be removed on exit.

## Mitigation and detection

- Restrict SMB and local admin accounts.
- Apply LAPS and segmentation.
- Monitor events 7045, 4688 and service creation.
- Alert on `PSEXESVC`, `ADMIN$` and remote execution.

## References

- <https://learn.microsoft.com/en-us/sysinternals/downloads/psexec>
- <https://attack.mitre.org/techniques/T1021/002/>
- <https://github.com/fortra/impacket>
