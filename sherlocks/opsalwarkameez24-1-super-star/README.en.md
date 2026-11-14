---
sherlock: "OpSalwarKameez24-1: Super-Star"
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, electron, app-asar, nodejs, websocket, shellcode]
---

# OpSalwarKameez24-1: Super-Star — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A phishing campaign distributes a fake discount coupon. The executable is an Electron app showing a coupon interface. Analyze the package and determine what it does on the host.

## Evidence

- `Electron-Coupon.exe` and its installer.
- `resources/app.asar`, `preload.js` and `script.jsc`.
- Network capture from the process.

```bash
file Electron-Coupon.exe
7z l Electron-Coupon.exe
```

## Investigation

### 1. Inventory and triage

Extract the installer and locate `app.asar`. `asar` packages JavaScript and resources; extracting it reveals `index.js`, `preload.js` and a native module.

```bash
npx asar extract app.asar app
ls -la app
```

### 2. Timeline

`index.js` creates a `BrowserWindow` with `nodeIntegration: true` and `contextIsolation: false`. The app opens a WebSocket and captures keystrokes from input fields. The channel and port appear in `preload.js`.

```bash
grep -RInE 'nodeIntegration|WebSocket|keydown|shellcode' app/
```

### 3. Key artifact

`script.jsc` contains bytecode and a base64 string. XOR with a short key produces shellcode; `strings` reveals `VirtualAlloc`, `RtlMoveMemory` and `CreateThread`. The shellcode connects to a C2 and runs `cmd.exe`.

## Conclusions

- The app is a keylogger with shellcode execution.
- Enabled `nodeIntegration` gives the renderer Node access.
- The C2 and fake coupon are the main IOCs.
- The Electron package must be treated as malware, not a legitimate app.

## Lessons

- `app.asar` is not encrypted; `asar` extracts it.
- `nodeIntegration` turns a web page into native code.
- A `.jsc` can hide shellcode and Windows APIs.
- Network capture confirms the exfiltration channel.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/luckystars0612/Sherlock-HTB/tree/main/SuperStar>
- <https://attack.mitre.org/techniques/T1056/001/>
