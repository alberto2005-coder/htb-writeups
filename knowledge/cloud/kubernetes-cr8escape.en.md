---
topic: Kubernetes — escape with cr8escape
tags: [cloud, kubernetes, cri-o, container-escape, cve-2022-0811]
---

# Kubernetes — escape with cr8escape

[🌐 Español](kubernetes-cr8escape.md) | **English**

## Concept

CVE-2022-0811 (cr8escape) allows injecting values into `kernel.core_pattern` through a pod's `sysctls` field. With a vulnerable CRI-O, the pattern is applied on the host and can run a binary when a process crashes.

## When it applies

- A cluster running CRI-O vulnerable to CVE-2022-0811.
- Permission to create pods with `securityContext.sysctls`.
- A node where the runtime can write `core_pattern`.

## Procedure

1. Confirm the runtime and the Kubernetes/CRI-O version.
2. Create a pod that injects `kernel.core_pattern`.
3. Place a binary or script on the host.
4. Trigger a core dump to fire the pattern.
5. Run commands on the node.

## Commands

```yaml
securityContext:
  sysctls:
  - name: kernel.core_pattern
    value: "|/tmp/payload"
```

## Variants

- Injection through `kernel.modprobe`.
- Pods with `privileged: true` and host mounts.
- Abusing `hostPath` to write the payload.

## Limitations

- The cluster must use a vulnerable CRI-O.
- The pod needs permission to set `sysctls`.
- Exploitation requires a core dump.

## Mitigation

- Patch CRI-O and Kubernetes.
- Apply Pod Security Standards and restrict `sysctls`.
- Avoid `privileged` and `hostPath`.

## Detection

- Pods with `kernel.core_pattern` or unusual `sysctls`.
- Core dumps and executions from `/tmp` on the node.

## References

- <https://kubernetes.io/docs/tasks/administer-cluster/sysctl-cluster/>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-0811>
