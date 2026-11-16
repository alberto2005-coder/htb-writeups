---
topic: IKE — aggressive mode and PSK cracking
tags: [network, ike, ipsec, vpn, psk, hashcat]
---

# IKE — aggressive mode and PSK cracking

[🌐 Español](ike-aggressive-psk.md) | **English**

## Concept

In IKEv1 aggressive mode, the initiator sends the proposal, Diffie-Hellman exchange, identity and a hash authenticated with the PSK in the first packet. The identity travels in clear and the hash allows testing PSK candidates without completing the handshake. It is the network equivalent of capturing a password hash.

## When it applies

- UDP/500 is open and answers IKE.
- The server allows aggressive mode (common with multiple groups or per-user PSKs).
- The PSK is weak or reused as a system password.

## Procedure

1. Confirm IKE with `ike-scan`.
2. Request the aggressive handshake and note the identity.
3. Save the material with `--pskcrack`.
4. Crack it with `hashcat -m 5400` and a wordlist.
5. Try the PSK against SSH, VPN or other services.

## Commands

```bash
ike-scan -A <IP>
ike-scan -A <IP> --pskcrack=handshake.txt
hashcat -m 5400 handshake.txt rockyou.txt
```

## Variants

- Identity brute force with `ike-scan -A -I <id>`.
- Dictionary attack with `psk-crack`.
- Use the PSK to establish the IPsec tunnel and pivot.
- Exposed TFTP/69 can hand over the router config and confirm the identity.
- Reuse the PSK against local accounts.

## Limitations

- Main mode does not leak the identity.
- IKEv2 with PSK is not vulnerable in the same way.
- A long, random PSK resists dictionaries.
- Some devices rate-limit or disable aggressive mode.

## Mitigation

- Use IKEv2 in main mode.
- Long, random per-user PSKs.
- Prefer certificates over PSKs.
- Never reuse network secrets as passwords.

## Detection

- Many aggressive handshakes from one IP.
- Invalid identities or UDP/500 scans.
- SSH authentication attempts with the PSK.
- Exposed TFTP/69 with network configurations.
- IKE traffic from hosts outside the VPN.

## References

- [RFC 7296 — IKEv2](https://datatracker.ietf.org/doc/html/rfc7296)
- [ike-scan — Documentation](https://github.com/royhills/ike-scan)
- [0xdf — Expressway](https://0xdf.gitlab.io/2026/03/07/htb-expressway.html)
