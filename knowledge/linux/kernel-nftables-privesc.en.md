---
topic: nftables kernel privilege escalation
tags: [linux, kernel, nftables, cve-2023-35001, privesc, uaf]
---

# nftables kernel privilege escalation

**English** | [🇪🇸 Español](kernel-nftables-privesc.md)

## Concept

CVE-2023-35001 is an out-of-bounds write in `nf_tables` that lets a local user manipulate kernel memory and elevate privileges. It affects certain 5.19 kernels and derivatives; Synacktiv's public exploit chains the corruption into a root escalation.

## When it applies

- A kernel within the vulnerable range.
- A local unprivileged user.
- `nf_tables` available.
- Ability to run a compiled exploit.

## Procedure

1. Confirm the kernel version.
2. Check whether `nf_tables` is loaded.
3. Verify the exploit matches the architecture.
4. Run it and check the identity.
5. Read privileged files or stabilise access.

```bash
uname -a
lsmod | grep nf_tables
gcc exploit.c -o exploit
./exploit
id
```

## Variants

- Adapting the exploit to another version or distribution.
- Using `unshare` to prepare namespaces.
- Chaining with a SUID shell or `setuid(0)`.
- Exploiting other nf_tables CVEs from the same period.

## Limitations

- The kernel must be in the affected range.
- KASLR and mitigations may require adjustments.
- The exploit can be unstable and cause a panic.
- A patched kernel invalidates the technique.

## Mitigation and detection

- Update the kernel.
- Restrict `unshare` and user namespaces.
- Apply memory protections and signed modules.
- Alert on compilations, new executables and kernel crashes.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2023-35001>
- <https://github.com/synacktiv/CVE-2023-35001>
- <https://attack.mitre.org/techniques/T1068/>
