---
topic: Port knocking — sequences and hidden services
tags: [linux, port-knocking, knockd, firewall, discovery]
---

# Port knocking — sequences and hidden services

**English** | [🌐 Español](port-knocking.md)

## Concept

`knockd` listens for a port sequence and, when received in order, adds a firewall rule opening a service. The sequence may leak in documentation, scripts or traffic. It is not authentication: it only hides the port until the order is known.

## When it applies

- An expected service does not respond and the firewall filters it.
- There are hints of a port sequence in code or notes.
- The host runs `knockd` or an equivalent script.

## Procedure

1. Search for the sequence in code, history or documentation.
2. Send the ports in order with `knock`.
3. Check that the service appears in a scan.
4. Connect before the rule expires.

## Commands

```bash
grep -R "knock\|sequence" /var/www /opt 2>/dev/null
knock <IP> 40809 50212 46969
nmap -Pn -sCV -p22 <IP>
ssh <USER>@<IP>
```

## Variants

- Use `nc -z` to send ports one by one.
- Automate the sequence with a script.
- Combine it with a source IP change.

## Limitations

- The sequence must be exact.
- The rule expires and must be repeated.
- The firewall may block the attacker.

## Mitigation

- Do not use port knocking as access control.
- Require strong authentication on the service.
- Monitor sequential scans.

## Detection

- Connections to closed ports in order.
- Temporary firewall rules.
- `knockd` on hosts that do not need it.

## References

- [knockd — manual](https://manpages.debian.org/testing/knockd/knockd.8.en.html)
- [0xdf — Oz](https://0xdf.gitlab.io/2019/01/12/htb-oz.html)
- [CWE-656 — Reliance on Security Through Obscurity](https://cwe.mitre.org/data/definitions/656.html)
