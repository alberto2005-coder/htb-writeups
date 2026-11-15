---
topic: Electron — updates and package signatures
tags: [windows, electron, updater, smb, code-signing]
---

# Electron — updates and package signatures

**English** | [🌐 Español](electron-updater-signature-bypass.md)

## Concept

Electron applications often update through `electron-updater`, reading a `latest.yml` manifest and downloading a package. If the update share is writable and the client does not validate the publisher signature, an attacker replaces the manifest and binary to execute code on the next check.

## When it applies

- An SMB or HTTP update share allows writes.
- The app uses `electron-updater` or a custom updater without signatures.
- The user opens the application or it checks for updates at startup.

## Procedure

1. Locate the manifest and update share.
2. Build a package with the same name and a higher version.
3. Replace `latest.yml` and the binary.
4. Wait for the check and verify execution.

## Commands

```bash
smbclient -N //<IP>/Software_Updates
# latest.yml points to the malicious package
cat latest.yml
# Publish the payload and manifest
smbclient -N //<IP>/Software_Updates -c "put latest.yml; put payload.exe"
```

## Variants

- Abuse an HTTP update path without TLS.
- Sign with a stolen or self-signed certificate if the client skips chain validation.
- Use a plugin or mobile app update channel.

## Limitations

- The client may validate the Authenticode signature.
- The share must be writable by the attacker.
- The version must be higher than the installed one.

## Mitigation

- Sign packages and validate signatures on the client.
- Serve updates over TLS with an allowlist.
- Restrict write access and monitor `latest.yml` changes.

## Detection

- `latest.yml` changes outside a deployment.
- Packages downloaded from unusual paths.
- Updater child processes launching new binaries.

## References

- [0xdf — Atom](https://0xdf.gitlab.io/2021/07/10/htb-atom.html)
- [Electron — autoUpdater](https://www.electronjs.org/docs/latest/api/auto-updater)
- [CWE-494 — Download of Code Without Integrity Check](https://cwe.mitre.org/data/definitions/494.html)
