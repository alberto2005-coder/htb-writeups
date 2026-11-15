---
machine: Skyfall
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, minio, vault, fuse, ssh-otp, privesc]
---

# Skyfall — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

MinIO 2023 is vulnerable to CVE-2023-28432 and leaks root credentials. They read a backup containing a Vault token whose policy allows generating SSH OTP credentials for `askyy`. `vault-unseal` runs with sudo and writes a root-owned `debug.log`; FUSE captures that log, reveals the master token, and provides access to root's SSH role.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 22.04 and `80/tcp` nginx serving `skyfall.htb`.
- The `demo.skyfall.htb` vhost hosts an application with login.
- `feroxbuster` finds `/metrics` and a blocked path pointing to MinIO.

## Enumeration

- A parsing inconsistency allows reaching MinIO through nginx.
- MinIO is vulnerable to CVE-2023-28432, leaking `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD`.
- Those credentials list buckets and download a `home_backup` archive.

## Foothold

The backup contains a `VAULT_TOKEN` in `.bashrc`. The token can list `ssh/*` and create credentials at `ssh/creds/dev_otp_key_role`; use `vault ssh` to log in as `askyy`.

```bash
curl -s http://demo.skyfall.htb/.../minio/bootstrap/v1/verify
export VAULT_ADDR=http://prd23-vault-internal.skyfall.htb
export VAULT_TOKEN=<TOKEN>
vault ssh --role dev_otp_key_role --mode otp --strict-host-key-checking=no askyy@skyfall.htb
```

## Lateral movement

`askyy` can run `vault-unseal` as root. The binary writes `debug.log` in the current directory with the master token; `askyy` cannot read it but can control where it is created.

## Privilege escalation

Mount a FUSE `memfs` with `AllowOther`, run `vault-unseal` inside and capture `debug.log` in an `askyy`-owned file. The master token allows reading root's SSH role and logging in as root.

```bash
./memfs out/ out
cd out && sudo /root/vault/vault-unseal -c /etc/vault-unseal.yaml -vd
cat debug.log | grep 'Master token'
vault ssh --role admin_otp_key_role --mode otp root@skyfall.htb
```

## Evidence

- MinIO with CVE-2023-28432 and root credentials.
- Backup with `VAULT_TOKEN` and SSH OTP as `askyy`.
- `debug.log` captured through FUSE and master token.

## Lessons learned

- An internal service reachable through parsing inconsistencies can leak secrets.
- Vault tokens need least privilege and must not live in dotfiles.
- FUSE can capture files a root process writes into a controlled directory.

## Mitigation and detection

- Update MinIO and isolate its API.
- Rotate Vault tokens and restrict SSH policies.
- Review FUSE mounts and binaries writing logs as root.

## References

- [0xdf — Skyfall](https://0xdf.gitlab.io/2024/08/31/htb-skyfall.html)
- [IppSec — Skyfall](https://www.youtube.com/watch?v=jceaFKZUNYY)
- [Hack The Box — Skyfall](https://app.hackthebox.com/machines/skyfall)
