---
topic: NTLM authentication
tags: [windows, ntlm, netntlmv2, relay, pass-the-hash, authentication]
---

# NTLM authentication

**English** | [🇪🇸 Español](ntlm-authentication.md)

## Concept

NTLM authenticates with a challenge and a response derived from the password. The server never receives the password, but an attacker can capture the challenge/response, relay it to another service or use the NTLM hash directly when the value is known.

## When it applies

- SMB, LDAP, HTTP or MSSQL with NTLM.
- SMB signing disabled.
- Internal traffic capture.
- Credentials in hash format.

## Procedure

1. Identify services accepting NTLM.
2. Check SMB signing.
3. Capture or relay an authentication.
4. Use the hash for Pass-the-Hash.
5. Crack NetNTLMv2 when relaying is not possible.

```bash
nxc smb <HOST> -u <USER> -p '<PASSWORD>' --shares
responder -I <IFACE> -wv
impacket-ntlmrelayx -tf targets.txt -smb2support
hashcat -m 5600 hashes.txt wordlist.txt
```

## Variants

- Captured and cracked NetNTLMv2.
- Relay to SMB, LDAP or MSSQL.
- Pass-the-Hash with NTLM.
- Authentication coercion with PetitPotam or PrinterBug.

## Limitations

- SMB signing blocks relaying.
- The hash must be valid and privileged.
- Segmentation limits movement.
- Authentication policies may require Kerberos.

## Mitigation and detection

- Enable SMB and LDAP signing.
- Disable NTLM where possible.
- Apply segmentation and LAPS.
- Alert on relayed authentications and hash use.

## References

- <https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview>
- <https://attack.mitre.org/techniques/T1550/002/>
- <https://github.com/lgandx/Responder>
