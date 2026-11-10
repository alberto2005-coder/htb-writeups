---
machine: Ignition
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, magento, default-credentials, linux, tier1]
---

# Ignition — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

A **Magento 2** store on **80/tcp** with the `ignition.htb` vhost. The `/admin` backend still uses weak credentials (`admin:qwerty123`): log in and the flag is on the dashboard.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
80/tcp open  http    nginx
```

```bash
echo "<TARGET_IP>    ignition.htb" | sudo tee -a /etc/hosts
```

- A single port: the web app.
- Browsing by IP fails: the app depends on the `Host` header, so the vhost is required.

```bash
whatweb http://ignition.htb
```

```text
Magento, nginx, PHP, Magento session cookies
```

## Enumeration

```bash
gobuster dir -u http://ignition.htb -w /usr/share/wordlists/dirb/common.txt
```

```text
/admin        (302 → /admin/adminhtml)
/setup        (blocked)
/errors
/robots.txt
```

- `/admin` redirects to the backend login (`adminhtml`).
- `/setup` is installed but protected: do not try to reinstall.
- No exploitable public catalogue: the target is the panel.

## Foothold

Magento requires passwords of at least 7 characters with a letter and a number. Try the usual suspects and the keyboard pattern the box hints at:

```text
username: admin
password: qwerty123
```

```bash
curl -s -c cookies.txt http://ignition.htb/admin/ -o /dev/null
```

Once logged in through the browser, the **Dashboard** shows the flag in the welcome block.

There is no shell: the chain ends at the panel. The weakness is **authentication**, not code execution.

## Lateral movement

- Not applicable: one service and no extra credentials.
- On a real Magento you would go for `app/etc/env.php` (MySQL credentials) after getting execution.

## Privilege escalation

- Not applicable: there is no operating-system access.
- Had RCE been achieved (malicious extension), the next step would be the `nginx`/`www-data` user.

## Evidence

- Screenshots of the login and the dashboard with the flag redacted.
- No real credentials in the repository.

## Lessons learned

- An unpatched CMS is not the only way in: a weak backend password is enough.
- Password policies (minimum length, letter and digit) do not prevent `qwerty123`.
- `robots.txt` and `/setup` confirm the product and version even when the panel is hidden.
- Enumerating the vhost first beats hammering the bare IP.

## Mitigations and detection

**How to fix it:**

- Strong unique passwords, MFA and lockout on the admin.
- Restrict `/admin` by IP or VPN and rename the backend path.
- Remove `/setup` after installation and keep Magento patched.
- Alert on logins from new locations.

**How it would be detected:**

- A run of failed `POST /admin/adminhtml` returning 302 followed by a 200 (successful guessing).
- Requests to `/setup` or `robots.txt` from external IPs.
- Admin sessions from non-corporate ASNs.

- CWE-1391: Use of Weak Credentials
- OWASP Top 10 2021: A07 Identification and Authentication Failures
- MITRE ATT&CK: [T1078.001](https://attack.mitre.org/techniques/T1078/001/), [T1110.001](https://attack.mitre.org/techniques/T1110/001/)

## References

- [Magento — Security best practices](https://experienceleague.adobe.com/docs/commerce-operations/security-and-compliance/security-best-practices.html)
- [OWASP — Credential Stuffing Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html)
