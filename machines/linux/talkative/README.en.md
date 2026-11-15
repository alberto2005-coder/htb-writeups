---
machine: Talkative
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, jamovi, rocket.chat, docker, capabilities, dac-read-search]
---

# Talkative — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The jamovi instance allows running R on the server and grants access to a container. Pivoting between containers reaches the host; a Rocket.Chat container with `CAP_DAC_READ_SEARCH` reads and writes files outside its tree and reaches root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443,3000 <IP>
curl -s http://talkative.htb/ | head
# R execution in jamovi
curl -s -X POST http://talkative.htb/run -d 'code=system("id")'
# Inside the container
capsh --print
mount | grep -E "host|docker"
cat /proc/1/root/etc/shadow 2>/dev/null
```

## Enumeration

- Jamovi reachable from the web with R script execution.
- Rocket.Chat in a container with broad capabilities.
- Mounts and sockets connecting containers to the host.

## Initial access

The jamovi editor accepts R code; run a command and obtain a shell in the container. From there, enumerate networks, variables and mounts to find the next hop.

## Privilege escalation

The Rocket.Chat container has `CAP_DAC_READ_SEARCH`, which bypasses file read permissions. Read host keys and configuration, write a privileged task or file, and execute as root.

## Evidence

- R execution in jamovi and container shell.
- `capsh --print` showing `cap_dac_read_search`.
- Host file read and root shell.

## Lessons learned

- Analysis editors with script execution are RCE by design.
- Capabilities amplify the impact of a compromised container.
- Host mounts turn a read into a privileged write.

## Mitigation and detection

- Isolate jamovi and disallow arbitrary scripts.
- Drop `CAP_DAC_READ_SEARCH` and mount secrets read-only.
- Segment containers and enforce seccomp/AppArmor.

## References

- [0xdf — Talkative](https://0xdf.gitlab.io/2022/08/27/htb-talkative.html)
- [Docker — Capabilities](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities)
- [Hack The Box — Talkative](https://app.hackthebox.com/machines/talkative)
