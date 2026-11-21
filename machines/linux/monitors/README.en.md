---
machine: Monitors
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, wordpress, lfi, cacti, cve-2020-14295, docker, ofbiz, cve-2020-9496, kernel-module, privesc]
---

# Monitors — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress runs the `wp-with-spritz` plugin, vulnerable to file inclusion. The LFI reads `wp-config.php` and obtains the database password, which is reused on the Cacti panel at `cacti-admin.monitors.htb`. Cacti is vulnerable to CVE-2020-14295: SQLi in `color.php` updates `path_php_binary` and runs commands when a reindex is forced. The shell is `www-data` on the host; the backup service reveals `marcus`'s password. On localhost, `docker-proxy` publishes an Apache OFBiz instance on `8443`, vulnerable to CVE-2020-9496 (Java deserialization in XML-RPC), giving root inside a privileged container. With `CAP_SYS_MODULE`, a kernel module is compiled and loaded to run commands as root on the host.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: Apache with WordPress and the Cacti vhost.

```bash
echo '<IP> monitors.htb cacti-admin.monitors.htb' | sudo tee -a /etc/hosts
wpscan --url http://monitors.htb --enumerate p
```

## Enumeration

`wpscan` finds `wp-with-spritz`, with unauthenticated file inclusion at `wp.spritz.content.filter.php?url=`:

```bash
curl -s 'http://monitors.htb/wp-content/plugins/wp-with-spritz/wp.spritz.content.filter.php?url=/../../../..//etc/passwd'
```

`wp-config.php` is read and the database password recovered. The same password works on Cacti as `admin`. Cacti is vulnerable to CVE-2020-14295.

## Foothold

The SQLi is in the `filter` parameter of `color.php`. It allows stacking a second query that changes configuration:

```text
/cacti/color.php?action=export&header=false&filter=1')+UNION+SELECT+1,username,password,4,5,6,7+from+user_auth;update+settings+set+value='<CMD>'+where+name='path_php_binary';--+-
```

A reindex then executes the value:

```text
/cacti/host.php?action=reindex
```

A reverse-shell command gives access as `www-data` on the host.

## Lateral movement

The `cacti-backup.service` unit runs `/home/marcus/.backup/backup.sh` as `www-data`; the script contains `marcus`'s password:

```bash
cat /etc/systemd/system/cacti-backup.service
cat /home/marcus/.backup/backup.sh
su marcus
```

As `marcus`, `ps` shows a `docker-proxy` publishing `127.0.0.1:8443` to another container. A tunnel reaches it and identifies Apache OFBiz. The version is vulnerable to CVE-2020-9496, unauthenticated Java deserialization at `/webtools/control/xmlrpc`.

A `ysoserial` payload (`CommonsBeanutils1`) downloads and runs a script; it is base64-encoded and sent inside the XML-RPC body. Execution is as root in the OFBiz container.

## Privilege escalation

The container is privileged and has `CAP_SYS_MODULE`. A kernel module is compiled against the host headers and loaded with `insmod`; it launches a reverse shell or creates a SUID bash and, because it runs in the host context, yields root outside the container.

## Evidence

- Plugin LFI and `wp-config.php` with the database password.
- Cacti access with reused credentials.
- SQLi in `color.php`, modified `path_php_binary` and RCE on reindex.
- OFBiz on `127.0.0.1:8443` and CVE-2020-9496 with `ysoserial`.
- Privileged container, loaded kernel module and root on the host.

## Lessons learned

- An abandoned plugin can expose the entire installation.
- Password reuse links WordPress and Cacti.
- SQLi with write access to `settings` becomes RCE.
- Internal services in containers are targets too.
- `CAP_SYS_MODULE` in a privileged container allows a host escape.
- Kernel modules run with maximum privileges.

## Mitigations and detection

- Remove unmaintained plugins and update WordPress and Cacti.
- Parameterize queries and restrict write access to configuration tables.
- Do not reuse passwords across applications.
- Segment internal services and never expose them unauthenticated.
- Avoid privileged containers and drop `CAP_SYS_MODULE`.
- Monitor `insmod`, `init_module` and modules outside the expected set.

## References

- [0xdf — Monitors](https://0xdf.gitlab.io/2021/10/09/htb-monitors.html)
- [Hack The Box — Monitors](https://app.hackthebox.com/machines/monitors)
- [NVD — CVE-2020-14295](https://nvd.nist.gov/vuln/detail/CVE-2020-14295)
- [NVD — CVE-2020-9496](https://nvd.nist.gov/vuln/detail/CVE-2020-9496)
- [Knowledge — CAP_SYS_MODULE escape](../../../knowledge/linux/cap-sys-module-escape.md)
