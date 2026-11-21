---
machine: Principal
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, spring-boot, pac4j, jwt, cve-2026-29000, password-spray, ssh-ca, privesc]
---

# Principal — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Spring Boot application uses pac4j for JWT authentication. CVE-2026-29000 forges encrypted JWTs using only the server's RSA public key (JWKS), bypassing signature verification and opening the dashboard. Settings expose an `encryptionKey` that is tried as an SSH password; a Hydra password spray finds it valid for `svc-deploy`. For root, the SSH CA private key in `/opt/principal/ssh`, owned by the `deployers` group, signs a certificate for the `root` principal and SSH logs in.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22`: OpenSSH 9.6p1 Ubuntu.
- `8080`: Jetty, Spring Boot application.

```bash
echo '<IP> principal.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://principal.htb:8080 -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The application has a login and a dashboard. The public configuration endpoint exposes the JWKS with the RSA key. The pac4j version is 6.0.3, older than the fixed releases for CVE-2026-29000.

Documentation and code show that JWTs are encrypted as well as signed, and that signature verification can be skipped when the token is encrypted with the public key.

## Foothold

CVE-2026-29000 builds an encrypted JWT with the server's public key and an arbitrary `sub`. The server decrypts it, does not validate the signature and accepts the identity. The token opens the dashboard as a privileged user.

Inside the dashboard, configuration shows an `encryptionKey` used to protect internal data. The user list is saved and a password spray is launched against SSH:

```bash
hydra -L users.txt -p '<ENCRYPTION_KEY>' ssh://<IP>
```

The key works for `svc-deploy`.

## Lateral movement

There is no second host. `svc-deploy` belongs to the `deployers` group. `/opt/principal/ssh` is owned by `root:deployers` and contains the SSH CA private key and its configuration.

## Privilege escalation

The CA key signs a certificate for the `root` principal. The server trusts certificates from that CA, so the certificate authenticates as root without knowing the password.

```bash
cd /opt/principal/ssh
ssh-keygen -t ed25519 -f /tmp/root
ssh-keygen -s ca -I root -n root /tmp/root.pub
ssh -i /tmp/root root@127.0.0.1
```

## Evidence

- Public JWKS and pac4j 6.0.3 version.
- Forged encrypted JWT and dashboard access.
- `encryptionKey` read from settings.
- Hydra password spray and SSH login as `svc-deploy`.
- `deployers` group and access to `/opt/principal/ssh`.
- Certificate signed for `root` and `id` with UID 0.

## Lessons learned

- An encrypted JWT does not replace signature verification; both must be validated.
- The public key is not a secret, but it must not allow forging identities.
- Reusing an encryption key as an SSH password is a serious flaw.
- A poorly protected SSH CA can issue certificates for any principal.
- Deployment groups need least privilege and auditing.

## Mitigations and detection

- Update pac4j to a fixed release and always validate signatures.
- Do not accept encrypted JWTs from untrusted issuers without checking `iss`, `aud` and algorithm.
- Separate encryption keys, signing keys and passwords; never reuse them.
- Protect the SSH CA private key with mode 600 and outside broad groups.
- Audit certificate issuance and requested principals.
- Alert on JWKS requests from external IPs, SSH sprays and certificates for `root`.

## References

- [0xdf — Principal](https://0xdf.gitlab.io/2026/03/30/htb-principal.html)
- [IppSec — Principal](https://www.youtube.com/watch?v=w0h0gkvOn0c)
- [Hack The Box — Principal](https://app.hackthebox.com/machines/principal)
- [NVD — CVE-2026-29000](https://nvd.nist.gov/vuln/detail/CVE-2026-29000)
- [Knowledge — pac4j-jwt authentication bypass](../../../knowledge/web/pac4j-jwt-auth-bypass.en.md)
