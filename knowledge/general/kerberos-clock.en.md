---
title: Kerberos and the clock — the 5-minute skew
tags: [kerberos, windows, active-directory, troubleshooting, lab]
---

# Kerberos and the clock: `KRB_AP_ERR_SKEW`

**English** | [🇪🇸 Español](kerberos-clock.md)

## 1. Why it matters

Kerberos rejects any ticket more than **5 minutes** off from the KDC. The error is explicit:

```text
KRB_AP_ERR_SKEW(Clock skew too great)
```

or, wrapped by tooling:

```text
Clock skew too great while getting initial credentials
```

It is not a credential failure: the password, hash or certificate may be perfectly valid. Check the time before touching anything else.

## 2. Check

```bash
date -u
timedatectl
```

Against the KDC or any service with a `Date` header:

```bash
curl -sI https://<host> | grep -i '^date'
```

Difference in seconds:

```bash
python3 - <<'PY'
from datetime import datetime, timezone
import email.utils, urllib.request
srv = urllib.request.urlopen('https://<host>').headers['Date']
print((email.utils.parsedate_to_datetime(srv) - datetime.now(timezone.utc)).total_seconds())
PY
```

## 3. Fix it in the lab

With NTP available:

```bash
sudo timedatectl set-ntp true
sudo systemctl restart systemd-timesyncd
```

On HTB the VPN blocks NTP (UDP/123), so set it by hand:

```bash
sudo date -s "$(curl -sI https://www.google.com | awk -F': ' '/^[Dd]ate/{print $2}')"
```

For a single command, without changing the system clock:

```bash
faketime '+8 hours' kinit '<user>@<DOMAIN>'
faketime -f '+8h' certipy req -u '<user>@<domain>' -p '<password>' -ca '<CA>' -template '<T>' -dc-ip <DC_IP>
```

## 4. The clock that reverts itself

If `timedatectl` shows the right time and seconds later it is wrong again, something is syncing from another source. On a VirtualBox VM the usual culprit is **`VBoxService`** (the `vboxadd-service` service, Guest Additions), which syncs with the host every few seconds:

```bash
systemctl status vboxadd-service      # LSB: VirtualBox Additions service
ps aux | grep -i VBoxService
sudo systemctl mask vboxadd-service
sudo service vboxadd-service stop
```

`systemd-timesyncd` is usually `inactive` and is not the problem: checking it and ruling it out saves time.

Other causes: `chronyd`/`ntpd` with an unreachable server, or the hypervisor itself (VMware Tools) with time sync enabled.

## 5. Related symptoms

- **`KRB_AP_ERR_MODIFIED`** → not the clock, but it shows up with stale PACs; after changing groups request a new ticket (`kvno`).
- **`Pre-authentication failed`** with a correct password → check case and realm, not the time.
- **Tickets that expire instantly** → clock far ahead: the ticket is born expired.
- **`Cannot contact any KDC`** → DNS or port 88, not the clock.

## 6. Detection and mitigation (defensive side)

- Keep `w32time`/`chronyd` on internal sources and monitor DC drift (`w32tm /monitor`).
- Alert on repeated `KRB_AP_ERR_SKEW`: it may indicate a compromised host or a misconfigured VM.
- In the lab, record the adjustment in your notes so you do not repeat the diagnosis.

Not an attack technique; MITRE does not apply.
