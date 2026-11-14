---
machine: Mirai
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, raspberry-pi, pihole, plex, default-credentials, deleted-file, usb]
---

# Mirai — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Raspberry Pi device running Pi-hole and Plex keeps the default Raspberry Pi credentials. User `pi` can run any command with `sudo`. The root flag was deleted from a mounted USB drive; it is recovered from the raw device with `grep`, `strings` or `extundelete`.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,53,80,1877,32400,32469 <IP>
```

- 22 SSH, 53 DNS, 80 HTTP, 1877 and 32469 UPnP, 32400 Plex.
- `X-Pi-hole` in HTTP responses and `/admin` confirm Pi-hole.
- Plex is exposed on 32400.

## Enumeration

```bash
curl -sI http://<IP>/
curl -s http://<IP>/admin/ | head
```

- Pi-hole has no default credentials, but the operating system does.
- The OpenSSH version suggests Debian 8.
- No direct web vector is found; the device itself is the target.

## Foothold

The official Raspberry Pi image keeps `pi` / `raspberry` when the password is not changed. Those credentials work over SSH.

```bash
ssh pi@<IP>
id
cat ~/Desktop/user.txt
```

The user flag is read; it is redacted here.

## Privilege escalation

`sudo -l` shows passwordless full permissions:

```bash
sudo -l
sudo -i
```

`/root/root.txt` does not contain the flag; it is a note about a backup on a USB drive. `mount` and `lsblk` show `/dev/sdb` mounted at `/media/usbstick`; `damnit.txt` confirms the flag was deleted.

```bash
mount | grep usb
ls -la /media/usbstick
```

Recover the flag from the raw device:

```bash
grep -aPo '[a-fA-F0-9]{32}' /dev/sdb
# or
strings /dev/sdb -n 32
```

A disk copy plus `extundelete` also works:

```bash
dd if=/dev/sdb of=usb.img
extundelete usb.img --restore-all
cat RECOVERED_FILES/root.txt
```

## Evidence

- `id` and `sudo -l` as `pi`.
- The `/root/root.txt` note and `mount` output.
- Recovery with `strings` or `extundelete`, flag redacted.

## Lessons learned

- IoT devices often keep factory credentials.
- `sudo ALL` turns a user account into direct root.
- Deleting a file does not erase its data from the device.

## Mitigations and detection

- Change the `pi` password and disable the default account.
- Restrict `sudo` and separate services from the system user.
- Encrypt removable media and never store secrets on it.
- Alert on `pi` logins, interactive `sudo` and unexpected USB mounts.

## References

- <https://www.hackthebox.com/machines/Mirai>
- <https://www.raspberrypi.com/documentation/computers/configuration.html>
- <https://attack.mitre.org/techniques/T1078/001/>
- <https://attack.mitre.org/techniques/T1552/>
