---
title: HTML smuggling and HTA — the file built in the browser
tags: [forensics, windows, html-smuggling, hta, dll-sideloading, phishing]
---

# HTML smuggling and HTA: the payload that is not an attachment

**English** | [🇪🇸 Español](html-smuggling-hta.md)

## 1. Why it evades filters

An email with a suspicious `.exe` or ZIP is blocked. In **HTML smuggling**, the attachment is an `.html` file with JavaScript that decodes a Base64 blob, creates a `Blob` and forces a ZIP/EXE download. The malicious file is never requested from the server: it is generated in the browser.

```html
<script>
const b64 = "<BASE64>";
const bytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
const blob = new Blob([bytes], {type: "application/octet-stream"});
const a = document.createElement("a");
a.href = URL.createObjectURL(blob);
a.download = "invoice.zip";
a.click();
</script>
```

The proxy sees HTML and JavaScript; the ZIP exists only on the user's disk.

## 2. HTA

An **HTA** (HTML Application) runs with `mshta.exe`, a signed Windows binary. It can contain VBScript/JScript and launch processes:

```html
<html><head><script language="VBScript">
CreateObject("WScript.Shell").Run "msoev.exe", 0, False
</script></head></html>
```

`mshta.exe` is a **LOLBin**: if policy allows, it runs the HTA without downloading another executable. It is invoked by double-click or from another script.

## 3. Typical chain

```text
email → downloader.html → ZIP → sheet.hta → mshta.exe
      → msoev.exe (decoy) → mso.dll / AppVIsvSubsystems64.dll
      → EmpireClient.exe → C2
```

- The PDF or invoice is the decoy.
- The legitimate EXE sits next to a malicious DLL with the expected name (**DLL side-loading**).
- The DLL loads the stager, which opens the command channel.

## 4. Forensic analysis

- **Procmon**: `Process Name is mshta.exe` and `Operation is Load Image`; then `msoev.exe` and DLLs from `Downloads`/`Temp`.
- **pcap**: DNS, SNI, periodic POSTs; `User-Agent` and path matter more than IP.
- **Downloads**: browser history, Zone.Identifier and `%TEMP%`.
- **Persistence**: Run keys, tasks, services and payload copies.
- **Hashes**: HTML, ZIP, HTA and DLLs; correlate across hosts.

## 5. Detection

- HTML with large Base64 blobs and `a.download`.
- `mshta.exe` with an argument in `Downloads`, `Temp` or a URL.
- DLLs loaded from user paths by signed processes.
- Periodic connections from a child of Office/browser.
- SmartScreen/Defender events and task creation.

## 6. Mitigation

- Block `mshta.exe` with AppLocker/WDAC unless approved.
- Inspect HTML and JavaScript, not just PE attachments.
- Enforce Mark-of-the-Web and SmartScreen; disallow execution from `Downloads`.
- Side-loading rules: DLLs only from `System32` or the app directory.
- Segment and monitor C2; isolate the host and rotate credentials.

MITRE: T1027.006, T1218.005, T1574.002, T1071.001.

## 7. References

- <https://attack.mitre.org/techniques/T1027/006/>
- <https://attack.mitre.org/techniques/T1218/005/>
- <https://0xdf.gitlab.io/2024/05/02/htb-sherlock-einladen.html>
