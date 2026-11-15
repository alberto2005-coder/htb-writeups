---
machine: Builder
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jenkins, cve, file-read, ssh]
---

# Builder — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Jenkins 2.441 is vulnerable to CVE-2024-23897: the CLI expands `@<path>` and allows file reads. The bcrypt hash for `jennifer` is extracted, cracked and used to access the panel, where a root SSH credential is hidden but recoverable. The key gives root access.

## Recon

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 22.04.
- `8080/tcp` Jetty with Jenkins; the `X-Jenkins` header confirms version `2.441`.
- `robots.txt` disallows the whole site and the panel shows a single user, `jennifer`.

## Enumeration

- Download `jnlpJars/jenkins-cli.jar` and list the available commands.
- CVE-2024-23897 replaces an `@file` argument with the file contents.
- `jennifer`'s hash is stored in `/var/jenkins_home/users/jennifer_*/config.xml`.

## Foothold

Use the CLI to read `config.xml` and extract the bcrypt hash. `hashcat -m 3200` cracks it; the password logs in to Jenkins.

```bash
java -jar jenkins-cli.jar -s http://<IP>:8080 help 0xdf
java -jar jenkins-cli.jar -s http://<IP>:8080 connect-node @/var/jenkins_home/users/jennifer_*/config.xml
hashcat -m 3200 hash.txt rockyou.txt
```

## Lateral movement

There is no other host. The pivot is from the Jenkins web account to the root SSH credential stored on the same server.

## Privilege escalation

The `root` credential is concealed in the edit form, but its encrypted value is sent to the browser. Decrypt it from the script console or recover it by running a pipeline with the SSH Agent plugin.

```bash
# Manage Jenkins -> Script Console
println(new String(javax.xml.bind.DatatypeConverter.parseBase64Binary('<BLOB>')))

# Or in a pipeline:
node { sshagent(credentials: ['1']) { sh 'cat /root/.ssh/id_rsa' } }
```

The private key provides SSH access as root.

## Evidence

- `X-Jenkins: 2.441` and CLI output containing the hash.
- Panel access as `jennifer`.
- Root private key and a `root@builder` prompt.

## Lessons learned

- The Jenkins CLI is a file-read surface when unpatched.
- A weak bcrypt hash on a service account allows panel access.
- Credentials hidden in forms are often sent to the client and can be recovered.

## Mitigation and detection

- Update Jenkins to a version fixed for CVE-2024-23897.
- Restrict the CLI and port `8080` to administrative networks.
- Rotate deployment credentials and audit their use in pipelines.

## References

- [0xdf — Builder](https://0xdf.gitlab.io/2024/02/12/htb-builder.html)
- [IppSec — Builder](https://www.youtube.com/watch?v=jYCOIf9Fcmo)
- [Hack The Box — Builder](https://app.hackthebox.com/machines/builder)
