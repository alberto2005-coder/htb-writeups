---
topic: SNMP — write community and remote execution
tags: [linux, snmp, net-snmp, rce, privesc]
---

# SNMP — write community and remote execution

**English** | [🌐 Español](snmp-write-rce.md)

## Concept

An SNMP community with write access allows changing `snmpd` configuration, including the `nsExtendOutput1Line` extension, which runs commands as the daemon user. Routes and monitoring scripts can also be modified.

## When it applies

- SNMP answers with a valid community.
- The community has `rw` on `NET-SNMP-EXTEND-MIB`.
- The daemon runs with useful privileges.

## Procedure

1. Enumerate communities with `onesixtyone` or `snmpwalk`.
2. Check write access to `nsExtend`.
3. Create an extension that runs a reverse shell.
4. Read output with `nsExtendOutput1Line`.

## Commands

```bash
onesixtyone -c communities.txt <IP>
snmpwalk -v2c -c <COMMUNITY> <IP> NET-SNMP-EXTEND-MIB::nsExtendObjects
snmpset -v2c -c <COMMUNITY> <IP> NET-SNMP-EXTEND-MIB::nsExtendCommand."pwn" s "/bin/bash"
```

## Variants

- Use `snmp-shell` to automate.
- Modify `nsExtendInput` to pass commands.
- Write to a monitoring script.

## Limitations

- The community may be read-only.
- `snmpd` may run as a user without a shell.
- The extension needs a restart in some versions.

## Mitigation

- Use SNMPv3 with authentication and read-only.
- Do not expose UDP/161 to the Internet.
- Run `snmpd` with least privilege.

## Detection

- `snmpset` on `nsExtend`.
- New extensions or child processes of `snmpd`.
- SNMP queries from unauthorized hosts.

## References

- [Net-SNMP — extend MIB](https://www.net-snmp.org/docs/mibs/NET-SNMP-EXTEND-MIB.txt)
- [0xdf — Intense](https://0xdf.gitlab.io/2020/11/14/htb-intense.html)
- [HackTricks — SNMP](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-snmp/index.html)
