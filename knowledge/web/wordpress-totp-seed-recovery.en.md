---
topic: Recovering the TOTP seed in WordPress
tags: [web, wordpress, totp, mfa, database]
---

# Recovering the TOTP seed in WordPress

[🌐 Español](wordpress-totp-seed-recovery.md) | **English**

## Concept

Two-factor plugins store the TOTP secret in the WordPress database, sometimes in plaintext or with a static key. With SQL access or a database dump, the current code can be generated and the second factor completed.

## When it applies

- Read access to `wp_users` and the 2FA plugin tables is available.
- The secret is not encrypted with a user-derived key.
- Login asks for a TOTP code after the password.

## Procedure

1. Enumerate tables and locate the 2FA plugin table.
2. Extract the target user's secret.
3. Generate the code with `oathtool` or `pyotp`.
4. Use the code in the verification prompt.

```sql
SELECT user_id, meta_key, meta_value FROM wp_usermeta WHERE meta_key LIKE '%totp%';
```

```bash
oathtool --totp -b '<SEED>'
python3 -c "import pyotp; print(pyotp.TOTP('<SEED>').now())"
```

## Variants

- Decrypt the secret with a key found in `wp-config.php`.
- Reuse the secret against another service.
- Disable the plugin from the database if writes are possible.

## Limitations

- The secret must be accessible.
- The code expires within seconds.
- Some plugins encrypt with a per-user key.

## Mitigation and detection

- Encrypt TOTP secrets with a key outside the database.
- Restrict SQL access and rotate secrets after an incident.
- Prefer passkeys or hardware tokens.

## References

- <https://datatracker.ietf.org/doc/html/rfc6238>
- <https://developer.wordpress.org/apis/security/>
- <https://attack.mitre.org/techniques/T1552/>
