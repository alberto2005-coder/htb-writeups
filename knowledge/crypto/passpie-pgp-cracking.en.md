---
topic: Cracking de Passpie con PGP
tags: [crypto, passpie, pgp, john, credentials]
---

# Cracking de Passpie con PGP

**English** | [🇪🇸 Español](passpie-pgp-cracking.md)

## Concept

Passpie encrypts passwords with a PGP key protected by a passphrase. If `.passpie` is accessible, the key can be extracted and cracked offline; the tool then decrypts the entries.

## When it applies

- A readable `~/.passpie` directory for the compromised user.
- A PGP key with a weak passphrase.
- Root or service passwords stored in Passpie.

## Procedure

1. Locate `.passpie` and the private key.
2. Extract the hash with `gpg2john`.
3. Crack it with John or Hashcat.
4. Use `passpie copy` to recover the credential.

```bash
ls -la ~/.passpie
gpg2john ~/.passpie/.keys > passpie.hash
john --wordlist=/usr/share/wordlists/rockyou.txt passpie.hash
passpie copy --to stdout
# Another entry:
passpie copy <SERVICE> --to stdout
```

## Variants

- PGP key without a passphrase.
- `.passpie` backup on a share or ZIP.
- Passphrase reused from another service.
- Entries exported in plaintext.

## Limitations

- The key must be available and not hardware-protected.
- A strong passphrase makes cracking impractical.
- Passpie versions may change the format.

## Mitigation and detection

- Protect `.passpie` with strict permissions and a strong passphrase.
- Use a hardware key or a manager with per-entry encryption.
- Rotate stored credentials after an intrusion.

## References

- <https://github.com/marcwebbie/passpie>
- <https://github.com/openwall/john/blob/bleeding-jumbo/doc/README.gpg>
- <https://gnupg.org/documentation/>
