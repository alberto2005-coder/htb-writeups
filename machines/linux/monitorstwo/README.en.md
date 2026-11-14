---
machine: MonitorsTwo
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, cacti, cve-2022-46169, docker, cve-2021-41091, suid]
---

# MonitorsTwo — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Cacti 1.2.22 is vulnerable to CVE-2022-46169: the `X-Forwarded-For` parameter allows unauthenticated command execution. The shell lands inside a Docker container with a SUID `capsh`, giving root in the container. MySQL credentials dump a hash and provide SSH as `marcus`; Docker is vulnerable to CVE-2021-41091, and a SUID bash copied from the container escalates on the host.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH and Cacti over HTTP.
- The Cacti version appears in responses and static files.
- The container exposes MySQL on the internal network.

## Enumeration

- Cacti 1.2.22 and `remote_agent.php` are reachable.
- The application trusts `X-Forwarded-For` for authorization.
- Inside the container, `capsh` has the SUID bit.
- `/var/www/html/include/config.php` contains MySQL credentials.

## Foothold

Send a request to `remote_agent.php` with an allowed IP and a `poller_id` that injects a command. The response runs a reverse shell as the web service user inside the container.

```bash
curl -s "http://<IP>/remote_agent.php?action=polldata&local_data_ids[]=1"   -H 'X-Forwarded-For: 127.0.0.1'
```

## Privilege escalation

SUID `/sbin/capsh` gives root in the container. Use the MySQL credentials to dump the user table, crack `marcus`'s hash and SSH to the host. Docker 20.10.14 is vulnerable to CVE-2021-41091: as container root, write a SUID bash into the overlay and execute it from the host.

```bash
find / -perm -4000 -type f 2>/dev/null
mysql -u <USER> -p -e 'select * from user_auth'
```

## Evidence

- Cacti response with the executed command.
- `id` as root inside the container.
- `marcus` hash and SSH session.
- SUID bash in the overlay and root on the host.

## Lessons learned

- A proxy header can become an authorization decision.
- A compromised container does not contain impact when the runtime is vulnerable.
- Always check Docker versions and container SUID files.

## Mitigations and detection

- Update Cacti and do not trust `X-Forwarded-For` without a validated proxy.
- Update Docker and restrict its API and mounts.
- Monitor `remote_agent.php` from external IPs and SUID creation.
- References: NVD CVE-2022-46169, CVE-2021-41091, HTB MonitorsTwo.

## References

- <https://www.hackthebox.com/machines/MonitorsTwo>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-46169>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-41091>
- <https://attack.mitre.org/techniques/T1190/>
