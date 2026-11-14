---
topic: FreeBSD — authpf and pf anchors
tags: [freebsd, pf, authpf, firewall, pivot]
---

# FreeBSD — authpf and pf anchors

[🌐 Español](authpf.md) | **English**

## Concept

`authpf` is a login shell that enables pf rules for an authenticated user. If the user can edit its anchor or configuration files, internal network access can be opened or firewall rules changed.

## When it applies

- `/etc/pf.conf` with `anchor "authpf/*"`.
- Users whose shell is `/usr/sbin/authpf`.
- Weak permissions on authpf anchors or files.

## Procedure

1. Review `/etc/pf.conf`, `/etc/authpf` and the user's shell.
2. Check whether the user can write to the anchor.
3. Log in over SSH to activate authpf.
4. Add rules to reach the internal network.
5. Verify with `pfctl -a authpf/<user> -sr`.

## Commands

```bash
cat /etc/pf.conf
grep authpf /etc/passwd
pfctl -a 'authpf/<USER>' -sr
ssh <USER>@<HOST>
```

## Variants

- Writable `authpf.rules` files.
- Rules allowing `rdr` or NAT.
- Reusing the session for pivoting.

## Limitations

- The user must authenticate successfully.
- pf must be loaded and the anchor enabled.
- Permissions may prevent writes.

## Mitigation

- Restrict writes under `/etc/authpf`.
- Review anchors and rules periodically.
- Limit authpf to specific users and networks.

## Detection

- New pf rules in authpf anchors.
- SSH sessions opening internal routes.

## References

- <https://man.freebsd.org/cgi/man.cgi?query=authpf>
- <https://docs.freebsd.org/en/books/handbook/firewalls/>
