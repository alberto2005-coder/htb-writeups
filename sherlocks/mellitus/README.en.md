---
sherlock: Mellitus
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, memory, volatility, chrome-history, hashdump, stego]
---

# Mellitus — Hack The Box Sherlock

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Pending confirmation on HTB without a session; reference writeup, not played.
> No flags, hashes or real credentials.

## TL;DR

The ZIP provides `memory_dump.vmem` and the VMware snapshot `memory_dump.vmsn`. Volatility 3 reconstructs processes, connections, Chrome history and local hashes. The chain involves a browser downloading an image; the image is inverted and hides the flag. Chrome history and recovered files provide context that memory alone does not.

## Setup

```bash
unzip mellitus.zip
file memory_dump.vmem memory_dump.vmsn
vol -f memory_dump.vmem windows.info
```

The `.vmsn` is the snapshot state: use it to validate `.vmem` consistency, not as an independent dump.

## 1. Processes and command lines

```bash
vol -f memory_dump.vmem windows.pslist
vol -f memory_dump.vmem windows.pstree
vol -f memory_dump.vmem windows.cmdline
```

Look for browser processes, recent downloads and executables in `Downloads`/`Temp`. Use the dump time as the reference; normalise every timestamp to UTC.

## 2. Network

```bash
vol -f memory_dump.vmem windows.netscan
```

Focus on browser connections and any user process reaching the Internet. Record them as `<REMOTE_IP>:<PORT>`; do not publish real IPs.

## 3. Chrome history

History lives at `Users/<USER>/AppData/Local/Google/Chrome/User Data/Default/History` (SQLite). Find it with `filescan` and dump it:

```bash
vol -f memory_dump.vmem windows.filescan | grep -i 'History'
vol -f memory_dump.vmem windows.dumpfiles --virtaddr <OFFSET>
sqlite3 History "select url,title,last_visit_time from urls order by last_visit_time desc limit 30;"
sqlite3 History "select target_path,tab_url from downloads;"
```

- `urls` gives the page and title.
- `downloads` gives the downloaded file and source URL.
- `visits` reconstructs the sequence, not just the last visit.

## 4. Hashes and credentials

```bash
vol -f memory_dump.vmem windows.hashdump
vol -f memory_dump.vmem windows.lsadump
```

Local hashes are recorded for the report but neither published nor cracked here. A new account or an out-of-context administrator hash is the finding.

## 5. The inverted image

The downloaded image looks odd: its colours are inverted. Fix it with ImageMagick or Pillow:

```bash
convert suspicious.png -negate fixed.png
python3 - <<'PY'
from PIL import Image, ImageOps
ImageOps.invert(Image.open('suspicious.png').convert('RGB')).save('fixed.png')
PY
```

After inverting, text or a code appears. Also check metadata and bit planes in case the flag is not only in the visible image:

```bash
exiftool suspicious.png
zsteg -a suspicious.png
```

## 6. Correlation

| Evidence | Question it answers |
|---|---|
| `pslist`/`cmdline` | what ran and with which arguments |
| `netscan` | where it connected |
| `History` | what the user downloaded and from where |
| `hashdump` | which credentials were in memory |
| inverted image | the final answer |

## Lessons learned

- The `.vmsn` snapshot does not replace `.vmem`, but helps date the state.
- Chrome history is SQLite and survives in memory; it is a goldmine for downloads.
- An “odd” image may just be colour inversion; try `-negate` before complex stego.
- Document local hashes carefully: they are not the flag and must not be published.
- Browser → download → file correlation is the main thread.

## Mitigations and detection

- Retain browser history and download telemetry on the endpoint.
- Alert on image downloads from uncategorised domains and later execution.
- Capture memory before powering off a compromised host.
- Detection: browser processes with anomalous connections, downloads into `Temp` and new local accounts.

MITRE: T1204.002, T1105, T1555.003, T1003. SAM.

## References

- <https://itsrad.io/blog/2025/Mellitus-Write-Up>
- <https://mwalkowski.com/post/sherlock-mellitus>
- <https://github.com/volatilityfoundation/volatility3>
