---
machine: Olympus
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, xdebug, aircrack-ng, port-knocking, docker, privesc]
---

# Olympus — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Xdebug 2.5.5 exposes port 9000 and allows PHP evaluation, giving `www-data`. From there, pivot to an Olympia container, capture 802.11 traffic and crack the `flightoficarus` key; that hint leads to SSH as `icarus` on 2222. A zone transfer and a note reveal port knocking to Hades, log in as `prometheus`, and the `docker` group allows mounting the host and becoming root.

## Recon

```bash
nmap -Pn -sCV -p22,53,80,2222 <IP>
nmap -Pn -sU -p53,161 <IP>
```

- `22` filtered, `2222` SSH, `53` DNS and `80` Apache.
- The site is a Zeus image with `index.php`.
- Headers include `Xdebug: 2.5.5`.

## Enumeration

- Xdebug accepts the `XDEBUG_SESSION` cookie and connects to port 9000.
- A DBGp client evaluates PHP and runs `system()`.
- `nc -e` is available on the host, so a `www-data` reverse shell follows.
- From the container, enumerate the internal network and the `olympia` container.

## Foothold

Access the Olympia container, which holds an 802.11 capture. `aircrack-ng` recovers the `flightoficarus` key; the note suggests user `icarus` and password `Too_cl0se_to_th3_Sun`. SSH on `2222` grants access.

```bash
aircrack-ng -w rockyou.txt capture.cap
ssh icarus@<IP> -p 2222
```

## Lateral movement

The container has `help_of_the_gods.txt`, and a DNS zone transfer reveals `ctfolympus.htb` with a note for `prometheus`: open a portal to Hades on ports `3456`, `8234` and `62431`, with password `St34l_th3_F1re!`.

```bash
for p in 3456 8234 62431; do nc -w1 <IP> $p; done
ssh prometheus@<IP>
```

## Privilege escalation

`prometheus` is in the `docker` group. Run a privileged container with the host filesystem mounted at `/mnt` and write a key to `/root/.ssh/authorized_keys`.

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## Evidence

- Xdebug and DBGp RCE.
- Olympia container and 802.11 capture.
- `icarus` over SSH and the Hades note.
- Port knocking and `prometheus`.
- `docker` group and root.

## Lessons learned

- Exposed Xdebug is remote PHP execution.
- Wireless captures can contain reusable passwords.
- Port knocking is obfuscation, not authentication.
- Membership in `docker` equals root on the host.

## Mitigation and detection

- Disable Xdebug in production and block port 9000.
- Never reuse WiFi keys as system passwords.
- Do not rely on port knocking; require real authentication.
- Restrict the `docker` group and use rootless containers.

## References

- [0xdf — Olympus](https://0xdf.gitlab.io/2018/09/22/htb-olympus.html)
- [IppSec — Olympus](https://www.youtube.com/watch?v=7ifJOon5-G8)
- [Hack The Box — Olympus](https://app.hackthebox.com/machines/olympus)
