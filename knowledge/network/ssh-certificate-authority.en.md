---
topic: SSH CA — key signing and impersonation
tags: [network, ssh, ca, certificates, privesc]
---

# SSH CA — key signing and impersonation

[🌐 Español](ssh-certificate-authority.md) | **English**

## Concept

An SSH server can trust a CA through `TrustedUserCAKeys`. Anyone who obtains the CA private key can sign a key with any principal, including root, and authenticate without knowing passwords.

## When it applies

- `/etc/ssh/sshd_config` with `TrustedUserCAKeys`.
- `ca` and `ca.pub` files readable by a user.
- Automation signing keys with a shared CA.

## Procedure

1. Look for `TrustedUserCAKeys` and `ca`/`ca.pub` files.
2. Check whether the CA private key is readable.
3. Sign a public key with the root principal.
4. Use the signed key to log in.
5. Inspect the certificate with `ssh-keygen -L`.

## Commands

```bash
ssh-keygen -t ed25519 -f user_key -N ''
ssh-keygen -s ca -I audit -n root -V +1d user_key.pub
ssh-keygen -L -f user_key-cert.pub
ssh -i user_key root@<HOST>
```

## Variants

- Wildcard principal or `*` in `AuthorizedPrincipalsFile`.
- Host certificates to impersonate servers.
- An old CA without revocation or `Serial`.

## Limitations

- The CA private key must be readable.
- `sshd` may restrict principals with `Match`.
- Certificates may be revoked through a KRL.

## Mitigation

- Protect the CA key and keep it off the server.
- Limit principals and use `AuthorizedPrincipalsCommand`.
- Configure revocation and short lifetimes.

## Detection

- Certificates signed outside the provisioning process.
- Root logins through a certificate with an unknown `Serial`.

## References

- <https://man.openbsd.org/sshd_config#TrustedUserCAKeys>
- <https://attack.mitre.org/techniques/T1550/>
