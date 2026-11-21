---
machine: Backfire
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, havoc, c2, ssrf, cve-2024-41570, hardhat, jwt, iptables, privesc]
---

# Backfire — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The file server on `8000` leaks the configuration of a Havoc server. CVE-2024-41570 is an unauthenticated SSRF in demon callback handling: the `COMMAND_SOCKET` and `COMMAND_PIVOT` commands are accepted without a prior `RequestID`, which allows opening a socket to Havoc's internal administration port. That socket speaks WebSocket and reaches the authenticated RCE, giving a shell as `ilya`. Her home contains a HardHatC2 installation with default settings; the default JWT secret forges a `Team Lead` token and executes commands as `sergej`. `sergej` can run `iptables` and `iptables-save` as root: a comment with newlines plus `iptables-save -f` writes an arbitrary file, which adds an SSH key for root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,443,8000,5000,7096 <IP>
```

- `22`: OpenSSH 9.2p1 Debian.
- `443`: nginx 1.22.1, web interface.
- `8000`: nginx, file server.
- `5000` and `7096`: filtered from outside; they will be seen from inside.

```bash
echo '<IP> backfire.htb' | sudo tee -a /etc/hosts
feroxbuster -k -u https://backfire.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

Port `443` returns an nginx `404` with the `X-Havoc` header, which identifies the product. The `8000` file server publishes documentation and configuration files, including the Havoc team server configuration with its key and listener. That leak enables the rest of the chain.

Inside the host, `netstat` shows `40056` (team server, localhost only) and `8443` (Havoc HTTP listener), plus ports `5000`/`7096`, which only accept local connections.

## Foothold

CVE-2024-41570 lets a forged demon open a socket on the team server without authentication. An agent is registered and the `COMMAND_SOCKET` and `COMMAND_PIVOT` commands are sent; they are accepted without checking the `RequestID`, resulting in a tunnel to `127.0.0.1:40056`. That tunnel speaks Havoc's WebSocket protocol and the authenticated RCE runs commands.

```text
Command 99 (DEMON_INITIALIZE) → register agent
COMMAND_SOCKET / COMMAND_PIVOT → tunnel to the internal panel
WebSocket + authenticated command → execution
```

The shell is `ilya`.

## Lateral movement

`/home/ilya` contains a note about HardHatC2: `sergej` installed it for testing and left the defaults. The process runs as `sergej` and the panel listens locally. HardHatC2's default JWT secret forges a `Team Lead` token; the token lives in browser local storage, and with it the panel executes a command and returns a shell as `sergej`.

## Privilege escalation

`sudo -l` shows two passwordless rules:

```text
(root) NOPASSWD: /usr/sbin/iptables
(root) NOPASSWD: /usr/sbin/iptables-save
```

`iptables-save` accepts `-f <file>` to write its output as root. Rules allow a free-form comment; if the comment contains newlines, the `iptables-save` dump writes those lines into the target file. A rule is added with an SSH public key as the comment and saved to `/root/.ssh/authorized_keys`:

```bash
sudo iptables -A INPUT -i lo -m comment --comment $'\n<PUBLIC_KEY>\n'
sudo iptables-save -f /root/.ssh/authorized_keys
ssh -i <KEY> root@backfire.htb
```

## Evidence

- Havoc configuration readable from the file server.
- Tunnel opened to `127.0.0.1:40056` with the socket commands.
- `id` execution as `ilya`.
- HardHatC2 note and process running as `sergej`.
- `Team Lead` token forged with the default secret.
- `sudo -l` with `iptables` and `iptables-save`.
- `/root/.ssh/authorized_keys` written and an SSH session as root.

## Lessons learned

- A C2 is software and can be vulnerable; it must be patched.
- Tunnel commands without state validation enable SSRF.
- Default JWT secrets turn a panel into an open door.
- `iptables-save -f` is arbitrary write when rule content is controlled.
- iptables comments accept newlines and must be filtered.

## Mitigations and detection

- Update Havoc and review commands that accept unauthenticated callbacks.
- Do not expose the administration panel; separate listeners from management.
- Change every default secret in HardHatC2 and any other C2.
- Do not grant `iptables-save` through `sudo`; use a wrapper that validates destination and content.
- Monitor writes to `/root/.ssh/authorized_keys` and rules with multiline comments.
- Alert on connections from the team server to internal ports.

## References

- [0xdf — Backfire](https://0xdf.gitlab.io/2025/06/07/htb-backfire.html)
- [IppSec — Backfire](https://www.youtube.com/watch?v=dZjd4XTms7E)
- [Hack The Box — Backfire](https://app.hackthebox.com/machines/backfire)
- [NVD — CVE-2024-41570](https://nvd.nist.gov/vuln/detail/CVE-2024-41570)
- [Knowledge — SSRF and RCE in Havoc C2](../../../knowledge/web/havoc-ssrf-rce.en.md)
