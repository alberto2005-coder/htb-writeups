---
topic: LDAP — filter injection in Active Directory
tags: [windows, active-directory, ldap, injection, enumeration, analysis]
---

# LDAP — filter injection in Active Directory

**English** | [🌐 Español](ldap-injection-ad.md)

## Idea

LDAP queries directories such as Active Directory. When an application concatenates user input into a filter, the metacharacters `(`, `)`, `*`, `\` and `|` change the query logic. Injection widens results, enumerates attributes and, if the application displays data, reads fields such as `description` or `info`, which sometimes hold passwords. On Analysis, the `name` parameter of an internal search page enumerated users and read a shared account's password.

## When it applies

- A web application authenticates or searches users against AD over LDAP.
- The parameter is reflected into the filter without escaping.
- The response changes with `*` or parentheses.
- The application account can read sensitive attributes.

## Procedure

1. Confirm behavior with `*`, `)(` and empty values.
2. Adjust the filter to return all objects or a specific attribute.
3. Enumerate users, groups and visible attributes.
4. Read `description`, `info`, `comment` and similar fields.
5. Reuse the credentials on the panel, SMB, WinRM or VPN.

## Commands

```text
name=*
name=*)(objectClass=user)(cn=*
name=*)(description=*
name=admin)(|(description=*
```

```bash
ldapsearch -x -H ldap://<DC> -D '<USER>@<DOMAIN>' -w '<PASSWORD>' \
  -b 'DC=<DOMAIN>,DC=<TLD>' '(objectClass=user)' description
```

## Variants

- Injection into the authentication filter to bypass the password.
- Blind injection through timing or status-code differences.
- `*` brute force of usernames and attributes.
- `LDAP://` queries from PowerShell to repeat enumeration.
- Abuse of attributes holding service-account passwords.

## Limitations

- The server may escape metacharacters or use parameterized queries.
- The application account may have minimal permissions.
- Sensitive attributes may be protected by ACLs.
- Injection does not always return data; sometimes only the result count changes.
- Queries are logged on the domain controller.

## Mitigation

- Parameterize LDAP queries and escape metacharacters.
- Allowlist the attributes that can be queried.
- Do not store passwords in `description` or readable attributes.
- Use least-privilege service accounts with auditing.
- Review dynamically built filters in the code.

## Detection

- Requests with `*`, `)(`, `|` or unbalanced parentheses in search parameters.
- LDAP queries returning more objects than expected.
- Reads of `description` or `info` from web accounts.
- LDAP errors exposed to the user.
- Spikes in user enumeration followed by authentication attempts.

## References

- [0xdf — Analysis](https://0xdf.gitlab.io/2024/06/01/htb-analysis.html)
- [OWASP — LDAP Injection](https://owasp.org/www-community/attacks/LDAP_Injection)
- [Microsoft — LDAP filters](https://learn.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax)
- [Analysis writeup](../../machines/windows/analysis/README.en.md)
