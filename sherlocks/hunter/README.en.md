---
sherlock: Hunter
domain: Threat Hunting
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [threat-hunting, dfir, windows, evtx, amcache, prefetch, keepass]
---

# Hunter — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; no platform answers.

## Scenario

A SOC analyst receives an alert about possible lateral movement and credential stuffing. Confidence is low because the SOC was just deployed, but network analysis confirms the attack. You get an endpoint triage image and an **incomplete** packet capture: the sensor had performance issues. The goal is to reconstruct the intrusion from initial access to exfiltration.

## Evidence

- Endpoint triage (partial disk image) with `Windows\System32\winevt\logs\System.evtx` and `Security.evtx`.
- `Windows\AppCompat\Programs\Amcache.hve`.
- `Prefetch\*.pf`, including `WHOAMI.EXE-*.pf` and `CERTUTIL.EXE-*.pf`.
- `ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb` (the Windows search index).
- The `C:\Users\alonzo.spire\` profile: Chrome (`User Data\Default`), Edge (`WebCache\WebCacheV01.dat`), `PSReadLine`, `FileZilla`, `NTUser.dat` and `UsrClass.dat`.
- A partial PCAP with FTP traffic to the attacker infrastructure.

```bash
sha256sum *.zip *.pcap     # record hashes before analysing
```

## Investigation

### 1. Inventory and triage

Start with the cheap timeline: services, logons and execution.

```bash
EvtxECmd.exe -f System.evtx --csv . --csvf system
EvtxECmd.exe -f Security.evtx --csv . --csvf security
PECmd.exe -d Prefetch --csv . --csvf prefetch
AmcacheParser.exe -f Amcache.hve --csv . --csvf amcache
```

- `System.evtx` shows a **7045** (service created): random name and `owUjOMCY.exe` under a user path.
- `Security.evtx` shows a **4624 type 3** (network) logon for `alonzo.spire` right after the 7045.
- `PECmd` dates the `whoami.exe` and `certutil.exe` runs; `AmcacheParser` gives the service executable's SHA1.

### 2. Timeline

Timezone is the trap: questions ask for UTC and EVTX records may be in the host's local time. Normalise everything to UTC before correlating.

1. Service creation and `owUjOMCY.exe` start (2023-06-21, morning).
2. Network logon by `alonzo.spire` (4624 type 3) and an immediate `whoami`.
3. `certutil` downloads `scout.bat` from the C2 and runs it.
4. The attacker RDPs in with administrator credentials (4624 type 10).
5. PowerShell enumeration and a KeePass dump.
6. FTP exfiltration and, after it fails, a cloud instance.

### 3. Key artifact

**PDF credentials without the PDF.** The Windows search index keeps content and metadata from documents that no longer exist. `SIDR` (Search Index DB Reporter) over `Windows.edb` recovers the indexed text of `Internal_Documentation.pdf`, including the administrator's RDP credentials.

```bash
SIDR.exe -f Windows.edb -o sidr.csv
```

**The rest of the chain** rests on user artefacts:

- `PSReadLine\ConsoleHost_history.txt`: the attacker runs `clean.ps1`; the cmdlets inside (`Get-NetDomainController`) show it is renamed PowerView.
- Chrome `History`: downloads of FileZilla, KeePass and Process Hacker; the jumplist shows the KeePass dump `pid9180.dmp`.
- `CryptnetUrlCache\MetaData` and `\Content`: `certutil` leaves the C2 URL and `scout.bat` itself, whose MD5 is computed from the recovered file.
- `FileZilla\filezilla.xml` and `recentservers.xml`: FTP host, user, password and remote path.
- `NTUser.dat` → `UserAssist`: FileZilla focus time (10 min 48 s = 648 s).
- `UsrClass.dat` → shellbags: a `Documents` folder holding the sensitive project ZIP.
- PCAP: the FTP stream carries `Keepassproc.zip` and `database.kdbx`; the ZIP is encrypted with the same password as the FTP server.

**From dump to content.** The KeePass dump falls to **CVE-2023-32784** (master password recovery from memory) and `keepass-password-dumper`. With the master password, `database.kdbx` opens, the project ZIP password is recovered, and inside are the note naming the internal application and the JSON with SSNs.

## Findings

- Initial access through a **Windows service** (T1569.002) running a randomly named binary; the 7045 plus the type 3 logon prove it.
- Recon with renamed PowerView, tools downloaded through the browser and `certutil` as a download cradle.
- Privilege escalation via **credentials in an indexed PDF**, then RDP as administrator.
- FTP exfiltration with FileZilla; after it failed, an attacker-owned cloud instance.
- KeePass database theft and CVE-2023-32784 abuse to open the project and personal data.
- Main IOCs: service and executable names, C2 URL, `scout.bat` hash, FTP host and path. The actual values stay in `private/`.

## Lessons

- **The search index is evidence**: `Windows.edb` keeps text from deleted documents; without it the PDF would be unrecoverable.
- **`CryptnetUrlCache` plus Prefetch**: the `certutil.exe` pair yields the download and its content even when the file is gone.
- **UserAssist and shellbags**: they quantify usage and visited folders without needing memory.
- **KeePass in memory**: a process dump plus CVE-2023-32784 equals the master password; disable process dumps and protect the laptop.
- **Partial capture**: with only part of the PCAP, endpoint artefacts carry the reconstruction. The organisation should revisit sensor sizing and retention.
