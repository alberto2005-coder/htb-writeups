---
topic: NetData ndsudo privilege escalation
tags: [linux, netdata, ndsudo, cve-2024-32019, path-hijack, suid]
---

# NetData ndsudo privilege escalation

**English** | [🇪🇸 Español](netdata-ndsudo.md)

## Concept

NetData's `ndsudo` helper is installed SUID root to run disk utilities. In affected versions it resolves the binary through `PATH` instead of using an absolute path (CVE-2024-32019), so a user in the `netdata` group can place an executable with the expected name and obtain root.

## When it applies

- NetData installed outside an updated package.
- `ndsudo` with the SUID bit.
- A user in the `netdata` group or with access to the helper directory.
- Calls such as `ndsudo nvme-list`.

## Procedure

1. Enumerate the user's permissions and groups.
2. Locate `ndsudo` and confirm SUID.
3. Review its strings and available subcommands.
4. Create a binary with the name of an expected utility.
5. Run the helper with a controlled `PATH`.

```bash
find / -perm -4000 -name ndsudo 2>/dev/null
strings /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo | grep -E '^[a-z][a-z-]*$'
PATH=/tmp/p:$PATH /opt/netdata/usr/libexec/netdata/plugins.d/ndsudo nvme-list
```

## Variants

- Hijacking `nvme`, `smartctl` or another invoked utility.
- Writing an ELF that calls `setuid(0)` and spawns a shell.
- Abusing the `netdata` group to read configuration or sockets.
- Enumerating other SUID helpers from the same product.

## Limitations

- The user must be able to write to a `PATH` directory.
- The fixed version uses absolute paths.
- The binary must keep the execute bit.
- AppArmor or SELinux may restrict execution.

## Mitigation and detection

- Update NetData and remove the `ndsudo` SUID bit when unnecessary.
- Run helpers with absolute paths and a sanitized `PATH`.
- Restrict the `netdata` group.
- Audit `ndsudo` executions and `PATH` changes in privileged processes.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2024-32019>
- <https://github.com/netdata/netdata/security/advisories>
- <https://attack.mitre.org/techniques/T1574/007/>
