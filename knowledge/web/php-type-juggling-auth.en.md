---
topic: PHP — type juggling and magic hashes
tags: [web, php, type-juggling, magic-hash, authentication]
---

# PHP — type juggling and magic hashes

**English** | [🌐 Español](php-type-juggling-auth.md)

## Concept

PHP converts numeric strings when comparing with `==`. A hash starting with `0e` followed by digits is interpreted as zero, just like another hash with the same shape. If the application compares hashes with `==`, a password can match the stored hash without knowing it.

## When it applies

- The login compares hashes with `==` or `!=`.
- The application uses MD5/SHA1 and not `password_verify`.
- The submitted password can be chosen.

## Procedure

1. Identify the comparison function and algorithm.
2. Try a known magic-hash password such as `240610708`.
3. Check whether the login accepts the session.
4. Use access to reach the upload or panel.

## Commands

```bash
# MD5(240610708) = 0e462097431906509019562988736854
curl -d "username=admin&password=240610708" http://<HOST>/login.php
# Other classic values
# QNKCDZO, aabg7XSs, aabC9RqS
php -r 'var_dump(md5("240610708"));'
```

## Variants

- Use SHA1 hashes with the same `0e` pattern.
- Abuse `strcmp` with arrays to skip comparison.
- Combine it with SQLi to obtain the stored hash.

## Limitations

- Only works with loose comparison, not `===`.
- The password must pass length or format validation.
- Modern PHP and frameworks use `password_verify`.

## Mitigation

- Use `password_hash` and `password_verify`.
- Compare with `===` and validate types.
- Enforce lockout and MFA on login.

## Detection

- Passwords with `0e...` hashes in login attempts.
- Authentication bypasses followed by uploads.
- Use of `==` in code reviews.

## References

- [PHP — Type juggling](https://www.php.net/manual/en/language.types.type-juggling.php)
- [0xdf — Falafel](https://0xdf.gitlab.io/2018/06/23/htb-falafel.html)
- [OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
