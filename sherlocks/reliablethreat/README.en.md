---
sherlock: ReliableThreat
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, vscode-extension, supply-chain, windows, powershell, persistence]
---

# ReliableThreat — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A seemingly legitimate Visual Studio Code extension starts running commands after an update. Reconstruct the infection chain, the affected files and the attacker's actions.

## Evidence

- VS Code extensions directory and installation history.
- PowerShell scripts and extension configuration files.
- Process, network and Windows persistence logs.
- Execution events and user-profile artefacts.

```bash
sha256sum <EXTENSION>.vsix
7z l <EXTENSION>.vsix
```

## Investigation

### 1. Inventory and triage

Locate the installed extension and compare its content with the public version. `package.json`, `extension.js` and helper scripts are the starting point.

```bash
Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Directory
Get-Content "$env:USERPROFILE\.vscode\extensions\<EXT>\package.json"
```

### 2. Timeline

- Extension installation or update.
- First child-process execution.
- Second-stage download.
- Persistence creation and outbound connections.

Correlate PowerShell events with processes started by `Code.exe`.

### 3. Key artefact

The extension activation script contains the download-and-execute logic. Deobfuscation reveals the URL, command and persistence path.

```powershell
Get-Content <EXT>\extension.js | Select-String -Pattern 'http|powershell|cmd|Run'
```

## Conclusions

- The legitimate extension was modified or impersonated.
- The first stage ran PowerShell from the editor process.
- The second stage established persistence and C2.
- IOCs: hash, URL, path and process name, redacted.

## Lessons

- Editor extensions are code with user privileges.
- An update can introduce malicious behaviour without changing the name.
- The chain is clearest when processes, network and persistence are correlated.

## References

- <https://www.hackthebox.com/sherlocks/ReliableThreat>
- <https://code.visualstudio.com/docs/editor/extension-marketplace>
- <https://attack.mitre.org/techniques/T1195/001/>
