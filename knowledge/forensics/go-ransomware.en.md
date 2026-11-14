---
topic: Go ransomware
tags: [forensics, malware, go, ransomware, aes-gcm, static-analysis]
---

# Go ransomware

**English** | [🇪🇸 Español](go-ransomware.md)

## Concept

Go binaries include the runtime, many strings and often build information. Go ransomware typically uses standard crypto libraries, embedded keys and directory walks. Static analysis can recover the key without running the sample.

## When it applies

- Large binaries with Go strings (`runtime.main`, `go.buildid`).
- Encrypted files with an appended extension.
- Ransom notes with payment instructions.
- Samples with HTTP C2 or webhooks.

## Procedure

1. Hash and identify the binary.
2. Extract strings and the Go version.
3. Locate the encryption function and key.
4. Review the algorithm and file format.
5. Decrypt a copy and verify the result.

```bash
file sample.exe
strings -n 8 sample.exe | grep -iE 'go1\.|AES|GCM|encrypt'
go version -m sample.exe
```

## Variants

- AES-GCM with embedded key and nonce.
- ChaCha20 or XOR with a derived key.
- Per-file encryption with a random nonce.
- Key sent to C2 before encryption.
- Ransomware spreading over network shares.

## Limitations

- The key may be encrypted by a loader.
- The binary may be packed or garbled.
- Without the original sample, decryption cannot be verified.
- Some variants delete the key after encryption.

## Mitigation and detection

- Immutable backups and restore testing.
- Block execution from user paths and email.
- Monitor mass file creation and anomalous extensions.
- Alert on processes walking many directories and webhook connections.

## References

- <https://attack.mitre.org/techniques/T1486/>
- <https://go.dev/doc/build-info>
- <https://pkg.go.dev/crypto/cipher>
- <https://www.cisa.gov/stopransomware>
