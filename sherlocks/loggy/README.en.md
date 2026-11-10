---
sherlock: Loggy
domain: Malware analysis
difficulty: Easy
platform: Hack The Box
evidence: Go binary, keylog and screenshots from a compromised host
tools: [Ghidra, strings, CyberChef, readpe]
state: Retired
tags: [dfir, malware, go, keylogger, ftp, exfiltration]
---

# Loggy — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

Janice from accounting was told by the SOC that her corporate credentials are on the dark web. Files are recovered from her machine and sent to the REM analyst. Reconstruct what the binary did, what it stole and where it sent it.

## Evidence

- `Loggy.exe`: PE32+ x86-64, 6.5 MB, MD5 `215e79eaa7b9ac16a7d2bce15c94b8de`.
- The screenshot and keylog file the binary produced on the host.

## Investigation

1. **Triage**: hash, type, compiler.

```bash
sha256sum Loggy.exe; file Loggy.exe
strings -n 8 Loggy.exe | grep -i "go1\." | head
```

The binary is written in **Go**: the runtime and `go/pkg/mod` paths give it away. That changes the approach (Ghidra plus `strings`, no classic Windows imports).

2. **Capabilities**: grepping the module paths exposes two telling repositories:

```bash
strings Loggy.exe | grep -i github
# github.com/kbinani/screenshot   -> screen capture
# github.com/jlaffaye/ftp         -> FTP client
```

3. **Keylogger**: the binary hooks the keyboard and **appends** keystrokes to `keylog.txt`. Janice's password change lands there, which is how the credentials leaked.

4. **Exfiltration**: `sendFilesViaFTP` logs in with **hardcoded** credentials to an external server and uploads the screenshots and the keylog.

```bash
strings Loggy.exe | grep -E ":21"
# <host>:21
```

5. **IOCs**: exfiltration host, attacker credentials, generated file paths and the module paths that fingerprint the tooling.

## Findings

- Go keylogger plus screen capture, exfiltrating over **clear-text FTP** on port 21.
- No persistence needed: the damage is credential theft, not encryption.
- The attacker's credentials are baked into the binary, which attributes the infrastructure.

## Lessons

- In Go binaries, module paths are a free capability list.
- A plain-text keylog in the user profile is direct evidence of stolen credentials.
- Outbound FTP from a workstation is an exfiltration signal almost no egress filter blocks.

## Pitfalls

- **Hunting classic imports**: Go has no useful Import Address Table; read strings and functions.
- **Running the sample**: isolated VM only; static analysis is enough here.
- **Host vs URL**: the dial string includes the port (`:21`); the answer is the domain alone.
