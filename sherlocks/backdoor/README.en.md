---
sherlock: Backdoor
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, iis, webshell, persistence, evtx]
---

# Backdoor — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

A compromised IIS server runs a webshell and leaves a persistence mechanism. The initial access is reconstructed from HTTP logs, the malicious file is located through the MFT, and execution is confirmed with EVTX and prefetch.

## Scenario

The response team detects anomalous traffic to a Windows web server. IIS logs, EVTX and a partial system image are provided to determine how the attacker entered and what they left behind.

## Artefacts

- IIS logs (`W3SVC`).
- Security, System and PowerShell EVTX.
- `$MFT`, prefetch and `Amcache`.
- `wwwroot` and temporary files.

## Methodology

1. Identify `POST` requests with suspicious parameters and odd user-agents.
2. Look for files created under `wwwroot` and compare hashes with the baseline.
3. Review events 4688, 7045 and 4104 around the first request.
4. Confirm webshell execution with prefetch/Amcache.
5. Enumerate `Run` keys, services and tasks created afterwards.

```bash
EvtxECmd.exe -d C:\\Evidence\\evtx --csv C:\\Evidence\\out
MFTECmd.exe -f C:\\Evidence\\MFT --csv C:\\Evidence\\mft
```

## Sample questions

- Which URI received the first malicious `POST`?
- Which file was created in the webroot?
- Which process executed the webshell?
- Which persistence mechanism was added?
- Which account was compromised?

## Tools

`EvtxECmd`, `MFTECmd`, `Timeline Explorer`, `PECmd`, `IIS Log Parser`.

## Evidence and redaction

Screenshots of requests, paths and the timeline are kept with IPs, users and filenames redacted.

## Lessons learned

- IIS logs reconstruct initial access.
- A new file in `wwwroot` signals a webshell.
- Persistence can outlive the web service restart.
- Temporal correlation prevents wrong attribution.

## Detection

- Alert on `POST` to executable extensions under `wwwroot`.
- Monitor file creation in web directories.
- Correlate 4688 with HTTP requests.
- Review services and tasks created after the incident.

## References

- <https://app.hackthebox.com/sherlocks/Backdoor>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://attack.mitre.org/techniques/T1547/001/>
