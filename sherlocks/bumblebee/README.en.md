---
sherlock: Bumblebee
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [malware-analysis, loader, iso, lnk, dll-sideloading]
---

# Bumblebee — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; platform answers are not reproduced.

## Scenario

A host runs an unknown loader delivered by email. The sample and host artefacts are provided; document the loading mechanism, the evasion techniques and the indicators to block it.

## Evidence

- The sample container (ISO/IMG or ZIP with an LNK).
- Accompanying binaries (a legitimate DLL plus a malicious one).
- Host artefacts: `Prefetch`, `Amcache`, execution history.

## Investigation

### 1. Container anatomy

**BumbleBee**-style loaders arrive in a container Windows mounts as a drive, holding a shortcut and a folder with the payload. Opening the LNK runs a legitimate binary (`rundll32`, `wscript`, a signed executable) that loads the malicious DLL from the same folder: **DLL sideloading**.

```bash
7z l sample.iso
7z x sample.iso -oextract/
file extract/*
cat extract/*.lnk | xxd | head
```

### 2. Execution chain

```bash
strings -n 6 extract/*.dll | head -40
```

Look for `AppData` paths, system process names and C2 strings. In the LNK, the arguments field reveals which legitimate binary is invoked and with what parameters.

### 3. Evasion

Loaders in this family usually check the machine's language/domain, delay with `Sleep`, and use `CreateProcess` with an obfuscated command line. Document each technique with the evidence supporting it, not by resemblance to other cases.

### 4. Correlate with the host

`Amcache` gives the executed binary's hash and path; `Prefetch` confirms it ran and how often. That answers whether a second stage was downloaded.

## Findings

- Email delivery with a container plus LNK and execution via DLL sideloading.
- Evasion built on environment checks and delays, not strong encryption.
- Indicators: binary names and hashes, extraction paths and C2 domains.

## Lessons

- ISO/IMG contents mount without `Mark-of-the-Web`: the user sees no warning.
- DLL sideloading abuses a signed binary; blocklisting by signature fails, watch the path.
- Documenting the technique with evidence prevents misattributing the sample to another family.
