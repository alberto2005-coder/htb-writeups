---
topic: ZeroLogon (CVE-2020-1472)
tags: [windows, active-directory, zerologon, netlogon, cve-2020-1472]
---

# ZeroLogon (CVE-2020-1472)

**English** | [🇪🇸 Español](zerologon.md)

## Concept

ZeroLogon is a critical Netlogon vulnerability. AES-CFB8 with an all-zero IV lets an attacker authenticate as a computer account without knowing its password. The usual target is a domain controller: reset the DC's computer-account password and gain access to dump credentials.

## When it applies

- A DC without the August 2020 patch.
- Netlogon reachable from the attacker's network.
- The domain lacks secure-channel enforcement.
- The goal is full domain compromise.

## Requirements and conditions

1. Connectivity to the DC (RPC/Netlogon).
2. DC name and computer account.
3. An exploitation tool (`zerologon`, Mimikatz, impacket).
4. Ability to restore the original password to avoid breaking the domain.

## Procedure

Test the bypass:

```bash
python3 zerologon.py <DC_NAME> <DC_IP>
```

On success, the computer account password is empty. Dump Administrator's hash:

```bash
impacket-secretsdump -just-dc -hashes :<NTLM_HASH> administrator@<DC_IP>
```

Use the hash with `psexec`/`wmiexec`. In a lab, restore the original password with the restore script or `netdom` to avoid breaking trust.

## Variants

- **Mimikatz**: `lsadump::zerologon` and `lsadump::dcsync`.
- **Impacket**: Netlogon and secretsdump modules.
- **Chained attack**: ZeroLogon to reset, DCSync to dump.
- **Direct DCSync**: if a user already has rights, ZeroLogon is unnecessary.

## Limitations

- Microsoft patched the vulnerability and added enforcement.
- The attack is destructive: changing the DC password can break replication.
- Modern DCs and domains with `FullSecureChannelProtection` are not vulnerable.
- Netlogon must accept the insecure channel.

## Mitigation

- Apply the CVE-2020-1472 patch.
- Enable enforcement (`FullSecureChannelProtection`).
- Segment DCs and restrict Netlogon.
- Monitor computer-account password changes.
- Document a restoration procedure.

## Detection

- Event 4742 (computer account changed) outside the change window.
- Anomalous Netlogon authentications and repeated errors.
- DC computer-account password changes.
- RPC/Netlogon traffic from non-admin hosts.
- Password-restore events and replication failures.

MITRE ATT&CK: T1068 (Exploitation for Privilege Escalation), T1003.006 (DCSync).

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2020-1472>
- <https://www.secura.com/blog/zero-logon>
- <https://attack.mitre.org/techniques/T1068/>
