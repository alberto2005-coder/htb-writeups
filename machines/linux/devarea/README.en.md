---
machine: DevArea
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, ftp, cxf, ssrf, cve-2022-46364, cve-2025-54123, privesc]
---

# DevArea — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Anonymous FTP hands over the JAR of an employee service. The SOAP service uses Apache CXF 3.2.14 and is vulnerable to CVE-2022-46364: an `xop:Include` with `href="file://..."` inside a `multipart/related` request reads server files. The read exposes the Hoverfly dashboard credentials, whose middleware command injection (CVE-2025-54123) gives a shell as `dev_ryan`. A SysWatch cookie forged with a readable secret and a weak filter reaches `syswatch`, and the double symlink in `syswatch.sh` reads root's private key.

## Recon

```bash
nmap -Pn -sCV -p21,22,80,8080,8500,8888 <IP>
```

- `21` anonymous FTP, `22` OpenSSH and `80`/`8080` web applications.
- `8500` is Hoverfly's proxy and `8888` its control dashboard.
- The FTP holds `employee-service.jar`; the WSDL is on `8080`.

## Enumeration

Decompile the JAR and review the WSDL at `http://<IP>:8080/employeeservice?wsdl`. The `submitReport` operation takes a `report` with `confidential`, `content`, `department` and `employeeName`. Hoverfly's process line (`ps`) and `/etc/systemd/system/hoverfly.service` expose the dashboard username and password, and its dashboard answers on `8888`.

## Foothold

The service ships CXF 3.2.14, older than 3.4.10/3.5.5. CXF only processes XOP when the envelope is the root part of a `multipart/related` message with type `application/xop+xml`. The `href` accepts `file:///etc/passwd` and the contents appear in the response.

```bash
curl -s http://<IP>:8080/employeeservice \
  -H 'Content-Type: multipart/related; type="application/xop+xml"; boundary="MIME_boundary"' \
  --data-binary @poc.xml
```

## Lateral movement

The Hoverfly dashboard credentials log in on `8888`. Hoverfly 1.11.3 and earlier runs the middleware command without validating it (CVE-2025-54123); a payload at `/api/v2/hoverfly/middleware` gives a shell as `dev_ryan`. Next, SysWatch: the session secret sits in a readable environment file, the cookie is forged and a `service` value bypasses the filter, granting access as `syswatch`.

```bash
ps auxww | grep -i hoverfly
curl -s http://<IP>:8888/
```

## Privilege escalation

The `logs/` directory is writable and `dev_ryan` can run `syswatch.sh logs` under sudo. `syswatch.sh logs <file>` resolves symlinks with `ls -l | awk '{print $NF}'`, which only follows one hop. A `flag.log -> redirect` link plus `redirect -> /root/.ssh/id_ed25519` passes validation and prints the private key, which grants root.

```bash
ln -s redirect flag.log
ln -s /root/.ssh/id_ed25519 redirect
sudo /opt/syswatch/syswatch.sh logs flag.log
```

## Evidence

- JAR downloaded over anonymous FTP.
- SOAP response containing `/etc/passwd`.
- Hoverfly credentials in the process line.
- Root key read through the double symlink.

## Lessons learned

- Build artefacts and anonymous FTP leak code and secrets.
- MTOM/XOP is only processed with the right `Content-Type`.
- Validating a symlink with `ls` does not resolve the whole chain; use `realpath`.
- A sudo script that accepts filenames is a trust boundary.

## Mitigation and detection

- Upgrade CXF to 3.4.10/3.5.5 or later and disable `file://` in `xop:Include`.
- Disable anonymous FTP and rotate the exposed credentials.
- Resolve paths with `realpath -e` and verify they stay inside the allowed directory.
- Audit `syswatch.sh` executions and SSH key reads.

## References

- [0xdf — DevArea](https://0xdf.gitlab.io/2026/07/04/htb-devarea.html)
- [IppSec — DevArea](https://www.youtube.com/watch?v=Unsgv70jpA4)
- [Hack The Box — DevArea](https://app.hackthebox.com/machines/devarea)
