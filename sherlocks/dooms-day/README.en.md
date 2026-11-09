---
sherlock: dOOMs Day
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, web, php2shell, cve, webshell, log-analysis]
---

# dOOMs Day — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

A PHP site managed by a third-party CMS shows new files and outbound traffic to an unknown host. The webroot, the access logs and the CMS database are provided; the job is to rebuild the **PHP2Shell** exploitation chain and measure what happened after access.

## Evidence

- Apache/nginx `access.log` and `error.log`.
- A copy of the webroot (including `.htaccess`, `uploads/`, `cache/`).
- A database export with the template or settings table.
- Optionally `last`, `auth.log` and the host's cron entries.

## Investigation

### 1. Find the opening request

PHP2Shell is abused through an HTTP request that injects code into a context the CMS later evaluates (template, cache, or serialised parameter). Hunt the anomalous shape in the log, not the generic `200`:

```bash
awk '{print $6, $7}' access.log | sort | uniq -c | sort -rn | head -30
grep -E "POST .*(template|cache|theme|module)" access.log | head
```

A `POST` to an admin endpoint with a script `User-Agent` (`python-requests`, `curl`) and a large body is the candidate. A 200 instead of 302/403 confirms authentication was bypassed.

### 2. Check whether the payload ran

```bash
grep -RIn "eval\|assert\|create_function\|preg_replace" webroot/ --include="*.php" | head -40
find webroot/ -newermt "2026-01-01" -type f -printf "%TY-%Tm-%Td %TH:%TM  %p\n" | sort
```

Files dated to the incident inside writable directories (`uploads`, `cache`, `tmp`, `sessions`) are the webshell. An `eval` over user-controlled data in the original CMS explains why it worked.

### 3. What the attacker did

```bash
grep -E "shell|cmd|upload|wget|curl" access.log | awk '{print $1, $4, $7}' | sort | uniq -c | sort -rn | head
```

Rebuild the sequence: webshell upload → recon (`whoami`, `id`, `uname -a`) → second-stage download → lateral movement or exfiltration. Requests to the webshell with `?cmd=` or `?c=` in the `GET` are the signature.

### 4. Persistence and scope

```bash
crontab -l; ls -la /etc/cron.*
grep -RIn "base64_decode\|gzinflate" webroot/ | head
```

Review scheduled tasks, newly created users (recent dates in `/etc/passwd`) and outbound connections for the period. Scope closes with the compromised CMS accounts: if the injection came from an account, rotate its credentials and the `APP_KEY`.

## Findings

- Access through PHP2Shell in the CMS, without valid credentials.
- A webshell in an upload directory where PHP execution was enabled.
- Minimal post-exploitation: reconnaissance plus a downloaded second stage.

## Lessons

- A CMS that writes templates or cache to disk and evaluates them is RCE when the directory does not block PHP.
- The line between a compromise and a scare lives in `access.log`: read the request body, not just the URL.
- Mitigation: `php_admin_flag engine off` in upload directories, WAF payload rules, and patch the CMS.
