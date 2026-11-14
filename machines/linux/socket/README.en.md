---
machine: Socket
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, websocket, sqlite, pyinstaller, sudo]
---

# Socket — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

QReader offers a desktop client packaged with PyInstaller. Unpacking and decompiling it reveals a WebSocket endpoint that talks to SQLite without parameterization. A UNION injection leaks `admin`'s hash, which is cracked for SSH as `tkeller`. The user may run a build script that invokes PyInstaller as root; a malicious `.spec` executes code and yields root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,5789 <IP>
```

- SSH, Flask/Werkzeug and a WebSocket service on 5789.
- `qreader.htb` and `ws.qreader.htb`.
- The site offers `QReader_lin_v0.0.2.zip` and the Windows build.

## Enumeration

- The Linux binary is a PyInstaller bundle.
- `pyinstxtractor` recovers `.pyc` files and `pycdc` reconstructs the code.
- The client sends its version to `ws://ws.qreader.htb:5789/version`.
- The SQLite query concatenates the received value.

## Foothold

Replicate the WebSocket message and inject a four-column UNION query. The users table returns `admin` and an MD5 hash; crack it, test reuse and log in over SSH as `tkeller`.

```bash
python3 -c 'import websocket; ...'
hashcat -m 0 <HASH> rockyou.txt
```

## Privilege escalation

`sudo -l` shows a `build-installer.sh` script run by root. It accepts a `.spec` and invokes PyInstaller; control the spec content and execute code during the root build. It can also copy a privileged file.

```bash
sudo /usr/local/sbin/build-installer.sh build <FILE>.spec
```

## Evidence

- Unpacked bundle and client code.
- WebSocket request with injection and returned rows.
- SSH session as `tkeller`.
- `sudo -l` and a PyInstaller build running as root.

## Lessons learned

- PyInstaller bundles do not hide source code.
- A WebSocket can be a full SQL API.
- Running builds as root turns a config file into code execution.

## Mitigations and detection

- Parameterize SQLite queries and validate message types.
- Do not trust a client because it is compiled.
- Build in an unprivileged container and review `.spec` files.
- Alert on root `pyinstaller` processes and writes to the build directory.
- References: HTB Socket, 0xdf, CWE-89.

## References

- <https://www.hackthebox.com/machines/Socket>
- <https://0xdf.gitlab.io/2023/07/15/htb-socket.html>
- <https://cwe.mitre.org/data/definitions/89.html>
- <https://attack.mitre.org/techniques/T1059/>
