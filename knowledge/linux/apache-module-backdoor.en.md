---
topic: Apache — malicious module and backdoored sshd
tags: [linux, apache, module, backdoor, sshd, reversing, privesc]
---

# Apache — malicious module and backdoored sshd

**English** | [🌐 Español](apache-module-backdoor.md)

## Concept

An attacker with root can add an Apache module that downloads and replaces system binaries such as `sshd`. The module loads through `LoadModule` and the modified binary contains a hidden password granting root access.

## When it applies

- Apache modules outside the catalog or with odd timestamps exist.
- `mods-enabled` points to a suspicious `.so`.
- `sshd` has a different size or hash.

## Procedure

1. List modules and check timestamps.
2. Analyze the `.so` with `strings` and a decompiler.
3. Identify the download URL and replaced binary.
4. Reverse the password XOR comparison.
5. Log in over SSH as root.

## Commands

```bash
apache2ctl -M
ls -l /usr/lib/apache2/modules/
cat /etc/apache2/mods-enabled/reader.load
strings -a /usr/lib/apache2/modules/mod_reader.so | less
# extract the bytes, XOR 0x96 and test the password
ssh root@<IP>
```

## Variants

- Modules hooking `auth_password`.
- Binary download from an external domain.
- Backdoor in PAM or a systemd service.

## Limitations

- The module may be hidden or unnamed.
- The binary may be patched differently.
- The password may require byte ordering.

## Mitigation

- Verify packages and modules with the package manager.
- Monitor changes to `/usr/lib/apache2` and `/usr/sbin/sshd`.
- Enforce file integrity and alerts.

## Detection

- New or out-of-package modules.
- Downloads from Apache.
- `sshd` hashes differing from the package.

## References

- [0xdf — Undetected](https://0xdf.gitlab.io/2022/07/02/htb-undetected.html)
- [Apache — modules](https://httpd.apache.org/docs/2.4/mod/)
- [MITRE — T1543](https://attack.mitre.org/techniques/T1543/)
