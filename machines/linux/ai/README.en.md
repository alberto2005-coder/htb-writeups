---
machine: AI
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, audio, jdwp, tomcat, privesc]
---

# AI — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site transcribes audio and feeds the recognised text into an unparameterised SQL query. The injection leaks credentials and gives SSH access as `alexa`. Tomcat runs as root with the JDWP debugger on `localhost:8000`; an SSH tunnel plus `jdwp-shellifier` executes commands as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH and `80` Apache.
- Tomcat (8080), MySQL 5.7 (3306) and JDWP (8000) listen on localhost only.
- The site accepts a `.wav` and returns the transcript and a search result.

## Enumeration

`gobuster` finds `ai.php`, `intelligence.php`, `db.php` and `/uploads`. `intelligence.php` documents the accepted voice model (US male) and `ai.php` is the upload form. `db.php` returns nothing on its own, suggesting it is included by another page.

## Foothold

Generate the audio with `flite` and submit it with `curl`. A phrase such as "open single quote" proves the text is concatenated into SQL. `union select` variants dump the version, tables and credentials. `alexa`'s credentials work over SSH.

```bash
flite -w /tmp/q.wav -voice rms -t "open single quote"
curl -s -X POST http://<IP>/ai.php \
  -F 'fileToUpload=@/tmp/q.wav;type=audio/x-wav' \
  -F 'submit=Process It!'
```

## Lateral movement

No pivot is needed: `alexa` is already on the host. `ps auxww` shows Tomcat started as root with `-agentlib:jdwp=transport=dt_socket,server=y,address=localhost:8000`.

## Privilege escalation

JDWP does not authenticate connecting clients. Forward the local port over SSH and use `jdwp-shellifier` to create a `Runtime` object and run a script.

```bash
ssh -L 223:localhost:8000 alexa@<IP>
python3 jdwp-shellifier.py -t 127.0.0.1 -p 223 --cmd '/dev/shm/x.sh'
```

## Evidence

- Transcript with an SQL error after a single quote.
- `ps` showing Tomcat as root and `address=localhost:8000`.
- `jdwp-shellifier` connection and a root shell.

## Lessons learned

- Voice is user input too: the transcript reaches SQL.
- A port bound to `localhost` is not safe when SSH is available.
- JDWP is remote code execution without authentication by design.
- Scripting the audio generation saves a lot of time during exploitation.

## Mitigation and detection

- Use parameterised queries and validate the recognised text.
- Never enable JDWP in production; if required, restrict it to a tunnel and authenticate the network path.
- Run Tomcat as an unprivileged user without capabilities.
- Alert on `-agentlib:jdwp` in process command lines and on connections to `8000`.

## References

- [0xdf — AI](https://0xdf.gitlab.io/2020/01/25/htb-ai.html)
- [IppSec — AI](https://www.youtube.com/watch?v=7n7YRntu3bc)
- [Hack The Box — AI](https://app.hackthebox.com/machines/ai)
