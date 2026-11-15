---
machine: BlockBlock
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, xss, ethereum, json-rpc, pacman, path-hijack]
---

# BlockBlock — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

XSS in the chat and a token-leaking endpoint allow admin access. The application queries an Ethereum blockchain; a block message contains SSH credentials. `forge` PATH hijacking and `pacman` complete the escalation.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,8545 <IP>
ffuf -u http://blockblock.htb/FUZZ -w /usr/share/wordlists/dirb/common.txt
# XSS in chat and token theft
curl -s -X POST http://blockblock.htb/api/chat -d '{"message":"<img src=x onerror=fetch('/api/token')>"}'
# Ethereum JSON-RPC
curl -s -X POST http://blockblock.htb:8545 -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",true],"id":1}'
forge --help
pacman -Qo /usr/bin/forge
```

## Enumeration

- Chat application with XSS and a token endpoint.
- Ethereum JSON-RPC node with readable blocks.
- User with `forge` and `pacman` permissions.

## Initial access

The XSS runs in the bot browser and steals the admin token. With the token, access the panel and query JSON-RPC; a block contains a message with SSH credentials.

## Privilege escalation

`forge` runs in a more privileged context and allows PATH hijacking. Then a `pacman` hook or install rule executed as root allows a malicious package to be created and root obtained.

## Evidence

- XSS callback with the token.
- `eth_getBlockByNumber` query with hex data.
- `forge` with manipulated PATH and `pacman` running the hook.

## Lessons learned

- A blockchain is a public, permanent data channel.
- A client-side token can become administrative access.
- Package managers with hooks execute privileged code.

## Mitigation and detection

- Sanitize chat and do not expose tokens on endpoints.
- Do not use the blockchain for secrets.
- Review `pacman` hooks and `forge` paths.

## References

- [0xdf — BlockBlock](https://0xdf.gitlab.io/2025/03/29/htb-blockblock.html)
- [Ethereum — JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/)
- [Hack The Box — BlockBlock](https://app.hackthebox.com/machines/blockblock)
