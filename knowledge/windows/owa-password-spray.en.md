---
topic: OWA — password spraying with enumerated users
tags: [windows, owa, exchange, password-spray, initial-access]
---

# OWA — password spraying with enumerated users

**English** | [🌐 Español](owa-password-spray.md)

## Concept

OWA exposes an Exchange authentication form. With a valid user list and one common password, many accounts are tested without crossing the per-account lockout threshold. Names can come from social media, the directory or email signatures.

## When it applies

- OWA is reachable and does not require MFA for every user.
- The lockout policy allows a few attempts per account.
- Names or email addresses for the organization are available.

## Procedure

1. Collect users from the website, LinkedIn or the application listing.
2. Choose a seasonal or weak password and try it once per account.
3. Verify valid credentials on OWA and on WinRM or SMB.
4. Use the account for internal phishing or to find more resources.

## Commands

```bash
# User list from the website or directory
python3 sprayingtoolkit.py -t https://<HOST>/owa/ -U users.txt -p '<PASSWORD>'
# Verify access
curl -k -I https://<HOST>/owa/
```

## Variants

- Try the password against VPN, RDP or WinRM as well as OWA.
- Build variants from the company name and year.
- Wait between rounds to avoid lockouts and detection.

## Limitations

- MFA or Conditional Access blocks access even with a valid password.
- The lockout policy may trigger after a few attempts.
- Accounts may require a password change at first logon.

## Mitigation

- Require MFA and smart lockout policies.
- Block common passwords and review distributed attempts.
- Limit name and email exposure on the website.

## Detection

- Many failed attempts distributed across accounts.
- Successful authentications from a new IP after failures.
- OWA access from unusual user agents or countries.

## References

- [0xdf — Reel2](https://0xdf.gitlab.io/2021/03/13/htb-reel2.html)
- [Microsoft — Outlook on the web](https://learn.microsoft.com/en-us/exchange/outlook-on-the-web/outlook-web-app)
- [MITRE T1110.003 — Password Spraying](https://attack.mitre.org/techniques/T1110/003/)
