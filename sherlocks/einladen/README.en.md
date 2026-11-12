---
sherlock: Einladen
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Retired
tags: [dfir, windows, html-smuggling, hta, dll-sideloading, procmon, pcap]
---

# Einladen — Hack The Box Sherlock

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (4 Apr 2024). Reference writeup; not played on this profile.
> No flags, hashes or real C2 domains.

## TL;DR

An email delivers `downloader.html`, which builds a ZIP in the browser via **HTML smuggling**. The ZIP contains a PDF decoy, an HTA, a legitimate executable and two DLLs for **DLL side-loading**. Execution chains `sheet.hta` → `msoev.exe` → malicious DLL → Empire stager. Procmon's `Logfile.PML` and `msoev.pcapng` reconstruct execution and command-and-control.

## Artefacts

| Artefact | Role |
|---|---|
| `downloader.html` | HTML dropper; builds the ZIP in memory |
| `sheet.hta` | Launcher; runs the decoy binary |
| `invoice.pdf` | Distraction document |
| `msoev.exe` | Legitimate executable used as a decoy |
| `mso.dll` | Malicious DLL loaded via side-loading |
| `AppVIsvSubsystems64.dll` | Support DLL / search-order abuse |
| `EmpireClient.exe` | Empire client/stager |
| `unc.js` | Bridge script to a remote resource |
| `Logfile.PML` | Procmon capture |
| `msoev.pcapng` | Network traffic from execution |

## 1. Email and dropper triage

Start with the date, sender and attachment name. `downloader.html` does not fetch a binary: obfuscated JavaScript decodes a Base64 blob, creates a `Blob` and forces a ZIP download. The browser never requests the ZIP from the server, so a URL-only proxy never sees it.

```bash
file downloader.html
grep -oE '[A-Za-z0-9+/=]{100,}' downloader.html | head
```

Extract the resulting ZIP into a working directory. Compute hashes for the record, but do not publish them.

## 2. Execution chain

The order observed in Procmon is:

```text
explorer.exe
  └─ mshta.exe sheet.hta
       └─ msoev.exe
            ├─ mso.dll
            ├─ AppVIsvSubsystems64.dll
            └─ EmpireClient.exe
```

- The HTA runs via `mshta.exe`, a Windows trusted binary.
- `msoev.exe` is legitimate and sits next to the malicious DLLs so the dependency search loads `mso.dll` before the system copy.
- `AppVIsvSubsystems64.dll` acts as a bridge or export proxy.
- The PDF the user opens is the decoy that justifies execution.

In Procmon, filter `Process Name is msoev.exe` and `Operation is Load Image`; this shows which DLL loads and from where. Also review `CreateFile`, `RegSetValue` and `TCP Send/Receive`.

## 3. Network

Open `msoev.pcapng` in Wireshark. Useful filters:

```text
dns
http.request
tls.handshake.extensions_server_name
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Identify the first beacon, its periodicity and the C2 host. Real domains and IPs are not copied into this writeup; they appear as `<C2_HOST>` and `<C2_IP>`. The `User-Agent` and POST path are more useful than the IP, which can rotate.

## 4. Persistence and scope

- `EmpireClient.exe` is copied to a user path and launched as a child of `msoev.exe`.
- Review Run keys, scheduled tasks and services created in the time window.
- `unc.js` may act as a bridge to invoke a UNC resource; check whether it generates SMB traffic.
- Look for other hosts with the same `downloader.html` or ZIP hash.

## 5. Timeline

| Time (UTC) | Event |
|---|---|
| T0 | Email with `downloader.html` received |
| T0+1m | Browser builds and downloads the ZIP |
| T0+2m | `mshta.exe` runs `sheet.hta` |
| T0+2m | `msoev.exe` loads `mso.dll` |
| T0+3m | First `EmpireClient.exe` beacon |
| T0+5m | Persistence and payload copy |

## Lessons learned

- HTML smuggling evades attachment inspection because the file is built client-side.
- Side-loading uses a signed executable and a DLL with the expected name.
- Procmon and pcap complement each other: one gives the process, the other the network.
- A PDF decoy is not the payload; it keeps the user from suspecting.
- Calling it “Empire” relies on the binary and beacon pattern, not a single string.

## Mitigations and detection

- Block `mshta.exe` and executables from user paths with AppLocker/WDAC rules.
- Alert on DLLs loaded from `Downloads`, `Temp` or `AppData` by signed processes.
- Inspect HTML with JavaScript that creates blobs and downloads; not just PE attachments.
- Detection: `mshta` → `msoev` → `EmpireClient`, periodic connections and task creation.
- Isolate the host, rotate credentials and hunt for the same dropper in email.

MITRE: T1027.006, T1218.005, T1574.002, T1071.001.

## References

- <https://0xdf.gitlab.io/2024/05/02/htb-sherlock-einladen.html>
- <https://attack.mitre.org/techniques/T1027/006/>
- <https://attack.mitre.org/techniques/T1574/002/>
