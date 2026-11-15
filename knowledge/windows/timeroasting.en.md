---
topic: Timeroasting — computer accounts over SNTP
tags: [windows, active-directory, timeroasting, ntp, kerberos]
---

# Timeroasting — computer accounts over SNTP

**English** | [🌐 Español](timeroasting.md)

## Concept

Timeroasting requests SNTP responses for computer accounts and obtains material derived from their password. The resulting hash is cracked offline and can provide access as the machine account, which often has domain privileges.

## When it applies

- The DC responds to SNTP and allows queries for computer accounts.
- Computer names or SIDs are known.
- Computer passwords are weak or old.

## Procedure

1. Enumerate computer accounts and their SIDs.
2. Request SNTP responses with `timeroast.py`.
3. Crack the hashes with Hashcat or John.
4. Use the machine account to enumerate and escalate.

## Commands

```bash
timeroast.py -d <DOMAIN> -u <USER> -p "<PASS>"
hashcat -m 31300 hashes.txt /usr/share/wordlists/rockyou.txt
# Alternative
john --format=timeroast hashes.txt
nxc smb <DC> -u '<MACHINE>$' -p "<PASS>"
```

## Variants

- Combine it with a domain user to enumerate SIDs.
- Use the machine account for RBCD or resource reading.
- Try the hash against other computers.

## Limitations

- Microsoft may require authentication for SNTP.
- Computer passwords rotate and may be strong.
- Cracking depends on entropy and the wordlist.

## Mitigation

- Restrict SNTP and require authentication.
- Rotate computer passwords and use managed accounts.
- Monitor anomalous SNTP queries.

## Detection

- Many SNTP requests for computer accounts.
- Machine-account logons from unusual hosts.
- Hashcat use against computer hashes.

## References

- [Secura — Timeroasting](https://www.secura.com/blog/timeroasting)
- [0xdf — RustyKey](https://0xdf.gitlab.io/2025/11/08/htb-rustykey.html)
- [MITRE — T1557](https://attack.mitre.org/techniques/T1557/)
