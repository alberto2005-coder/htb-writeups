---
machine: Validation
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, second-order-sqli, cookies, upload, uhc]
---

# Validation — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The registration app stores the username unsanitised and uses it in a later query (second-order SQLi). The injection dumps credentials and grants access to an upload panel; a webshell and a permission misconfiguration lead to root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Add `validation.htb` to hosts. The site allows registration and shows a profile panel. Review cookies and parameters.

## Initial access

The `username` field accepts a SQL payload that is stored and executed when the profile is queried. Use a UNION or error-based payload to dump users and passwords. The credentials grant access to the admin panel.

Alternative with `sqlmap` against the login/profile request:

```bash
sqlmap -r request.txt --level 5 --risk 3 --batch
```

## Lateral movement

The panel allows file upload. Upload a PHP webshell and execute it:

```bash
curl 'http://validation.htb/uploads/shell.php?c=id'
```

This returns a shell as the web service user.

## Privilege escalation

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
```

Identify a SUID binary or a misconfigured sudo rule. Abuse it (for example, a script calling a binary without an absolute path) to get root. Read and redact the flag.

## Evidence

- Registration request with the SQL payload (redacted).
- Credential dump redacted.
- Webshell and `sudo -l`/SUID.
- Root shell and redacted flag.

## Lessons learned

- Sanitising at registration is not enough if the value is used later.
- Cookies and profiles are second-order SQLi points.
- An unvalidated upload panel enables RCE.
- Review SUID/sudo after foothold.

## Mitigation and detection

- Parameterised queries at every layer.
- Validate uploaded file type and content.
- Store uploads outside the webroot without execution.
- Audit SUID and sudo rules.

## References

- <https://www.hackthebox.com/machines/validation>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://gtfobins.github.io/>
