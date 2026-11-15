---
machine: Calamity
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, php, stego, suid, buffer-overflow]
---

# Calamity — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A page that executes arbitrary PHP provides the web foothold. Audio steganography reveals an SSH password. Escalation exploits a SUID binary with staged buffer overflows to control the flow and run as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
gobuster dir -u http://calamity.htb -w /usr/share/wordlists/dirb/common.txt
curl -s "http://calamity.htb/admin.php?cmd=id"
# Steganography
steghide extract -sf audio.wav
audacity audio.wav
# SUID
find / -perm -4000 -type f 2>/dev/null
checksec --file=/usr/local/bin/<BIN>
gdb -q /usr/local/bin/<BIN>
python3 exploit.py
```

## Enumeration

- PHP application with an accessible code editor or executor.
- Audio file with hidden data and an SSH user.
- Non-standard SUID binary with controllable input.

## Initial access

Find a page that evaluates PHP and use it to run commands. Locate an audio file on the system; `steghide` or Audacity extracts a string that turns out to be an SSH password.

## Privilege escalation

`find / -perm -4000` shows a custom binary. `checksec` confirms NX and a canary, but the program chains reads and overflows in stages that leak addresses and overwrite the return address. Build the exploit with pwntools and run it for root.

## Evidence

- PHP execution and initial shell.
- Audio with the extracted password.
- Address leak, return offset and root shell.

## Lessons learned

- Steganography remains a secret channel.
- A SUID with user input requires memory auditing.
- Staged leaks turn a canary into a surmountable obstacle.

## Mitigation and detection

- Do not allow PHP execution from the web.
- Remove unnecessary SUID binaries and build with full mitigations.
- Do not hide credentials in public files.

## References

- [0xdf — Calamity](https://0xdf.gitlab.io/2020/08/27/htb-calamity.html)
- [GDB — Debugging](https://sourceware.org/gdb/documentation/)
- [Hack The Box — Calamity](https://app.hackthebox.com/machines/calamity)
