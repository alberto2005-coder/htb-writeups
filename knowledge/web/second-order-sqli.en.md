---
topic: Second-order SQLi — stored injection executed later
tags: [web, sqli, second-order, union, earlyaccess]
---

# Second-order SQLi — stored injection executed later

[🌐 Español](second-order-sqli.md) | **English**

## Idea

In a second-order SQLi the payload is stored in the database in a first step and used unparameterized in a later query. The request that inserts it shows no error and changes nothing, so scanners that only inspect the immediate response miss it. On EarlyAccess the username was stored at registration and interpolated later when generating a key.

## When it applies

- A field is stored and later reused in another query (profiles, names, references).
- The first operation validates format but does not escape SQL characters.
- A function reads the stored value and builds a query with it.
- The error or behavioural difference appears on a screen other than the input one.

## Procedure

1. Map the fields that are stored and later displayed or processed.
2. Insert a single quote and check whether the second step fails or changes.
3. Confirm with a true and a false condition.
4. Build a UNION with the right column count.
5. Extract hashes, emails or tokens and reuse them.

## Commands

```text
username: test' AND 1=1-- -
username: test' AND 1=2-- -
```

```sql
' UNION SELECT 1,username,password,4,5 FROM users-- -
```

```bash
sqlmap -u "https://<HOST>/<PATH>" --data="username=<PAYLOAD>&password=x" --batch --dump
```

## Variants

- Store the payload in a record and trigger the query with a later login.
- Inject into a field used as a table or column name.
- Combine it with a password or role change to observe the effect.
- If filters exist, encode the payload or use equivalent functions.

## Limitations

- Column count and types must match the target query.
- The application may escape at the second step even if it did not at the first.
- The effect may require privileges or a specific flow.
- Logs may retain the stored payload.

## Mitigation

- Parameterize every query, including those reading already stored data.
- Validate and normalize fields on input and on output.
- Use an ORM with prepared statements and avoid dynamic SQL.
- Limit the database account's privileges.
- Review flows that reuse user data in queries.

## Detection

- Quotes, SQL comments and `UNION` in stored fields.
- SQL errors on screens other than the input form.
- Queries concatenating values that come from the database.
- Behavioural differences between records with and without the payload.

## References

- [OWASP — SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PortSwigger — Second-order SQL injection](https://portswigger.net/web-security/sql-injection)
- [0xdf — EarlyAccess](https://0xdf.gitlab.io/2022/02/12/htb-earlyaccess.html)
- [EarlyAccess writeup](../../machines/linux/earlyaccess/README.en.md)
