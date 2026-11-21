---
topic: Active Directory — Get-bADpasswords, certificates and DCSync
tags: [windows, active-directory, dcsync, certificate, code-signing, kerberos, hathor]
---

# Active Directory — Get-bADpasswords, certificates and DCSync

**English** | [🌐 Español](badpasswords-dcsync.md)

## Idea

`Get-bADpasswords` audits weak passwords in Active Directory and needs replication rights (DCSync) to read hashes. If a privileged task runs a modifiable script signed with a valid certificate, that account can be made to execute code. On Hathor, a code-signing certificate recovered from the recycle bin modified the script and ran it as `bpassrunner`; DCSync followed and, since NTLM was disabled, Kerberos tickets were used.

## When it applies

- A scheduled task runs an audit script as a privileged user.
- The script is modifiable or replaceable.
- A code-signing certificate is available (recycle bin, shares, backups).
- The account has replication rights or a ticket can be obtained.

## Procedure

1. Locate the task, the script and the user running it.
2. Check whether the script is signed and whether the signature is validated.
3. Obtain a signing certificate and its key.
4. Modify the script and sign it again.
5. Wait for the scheduled run and execute as that account.
6. Run DCSync and use the hash or a Kerberos ticket.

## Commands

```powershell
Get-ScheduledTask | Where-Object { $_.Actions.Execute -match 'powershell|vbs|cmd' }
Get-AuthenticodeSignature C:\Get-bADpasswords\run.vbs
```

```powershell
Get-ADReplAccount -SamAccountName administrator -Server '<DC>'
```

```bash
getTGT.py -hashes :<NTHASH> <DOMAIN>/administrator
KRB5CCNAME=./administrator.ccache evil-winrm -i <DC> -r <DOMAIN>
```

## Variants

- Replace the script with a binary or `.lnk` if the task allows it.
- Use `signtool` with an exportable certificate and its password.
- DCSync with `mimikatz` (`lsadump::dcsync`) instead of `Get-ADReplAccount`.
- Pass-the-hash when NTLM is enabled.
- `gettgt`/`getST` to obtain tickets from the hash.

## Limitations

- The signature must be valid and the certificate unexpired.
- The task may run as an account without replication rights.
- DCSync requires replication rights or domain privileges.
- Disabled NTLM prevents direct hash use.
- Script modification may be logged.

## Mitigation

- Protect audit scripts with read-only permissions.
- Validate signature and publisher in scheduled tasks.
- Remove code-signing certificates from recycle bins, shares and backups.
- Limit replication rights to specific accounts.
- Audit DCSync and Kerberos ticket use.

## Detection

- Modified signed scripts or invalid signatures.
- `Get-bADpasswords` running outside its usual window.
- DCSync from hosts that are not domain controllers.
- Ticket requests for privileged accounts.
- Code-signing certificates used after revocation.

## References

- [0xdf — Hathor](https://0xdf.gitlab.io/2022/11/19/htb-hathor.html)
- [GitHub — Get-bADpasswords](https://github.com/malteposener/Get-bADpasswords)
- [MITRE — DCSync](https://attack.mitre.org/techniques/T1003/006/)
- [Hathor writeup](../../machines/windows/hathor/README.en.md)
