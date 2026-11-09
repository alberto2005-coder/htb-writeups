---
challenge: Extraterrestrial Persistence
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, linux, systemd, persistence, base64]
---

# Extraterrestrial Persistence — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A shell script installs Linux persistence: it downloads a binary to `/usr/local/bin/service`, writes a **systemd unit** from a **base64** blob and enables it. Decoding the blob reveals the `.service`, and its `Description` holds the flag.

## Evidence

- `persistence.sh`.

## Method

1. **Read the script**: it first checks `whoami`/`hostname` to run only on the expected host, then downloads and stages the unit.

```bash
cat persistence.sh
```

2. **Find the blob**: there is an `echo -e "<base64>" | base64 --decode > /usr/lib/systemd/system/service.service`.

3. **Decode** without executing anything:

```bash
echo '<base64>' | base64 -d
```

```ini
[Unit]
Description=<flag>
After=network.target network-online.target
...
```

4. **Read the persistence**: `Type=oneshot` with `RemainAfterExit=yes` and `WantedBy=multi-user.target` runs the binary on every boot; `systemctl enable` creates the link.

## Pitfalls

- **`echo -e`**: escaped newlines can bite; decode from a file with `base64 -d`.
- **Double encoding**: if the output does not start with `[Unit]`, there is another layer.
- **Do not run it**: analysis is static; executing downloads and activates a binary.

## Lessons

- Persistence scripts usually ship their own installer; reading it gives the whole mechanism.
- A `base64` blob in an `echo` is trivial obfuscation: one line undoes it.
- A `oneshot` unit with `RemainAfterExit` is quiet persistence.
