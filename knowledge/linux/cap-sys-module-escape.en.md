---
topic: Linux — container escape with CAP_SYS_MODULE
tags: [linux, docker, capabilities, kernel-module, container-escape]
---

# Linux — container escape with CAP_SYS_MODULE

**English** | [🌐 Español](cap-sys-module-escape.md)

## Concept

`CAP_SYS_MODULE` allows loading and unloading kernel modules. A container with this capability is not isolated from the host: it can build or copy a module that runs code in kernel mode and gain full control. It is more powerful than many `--privileged` configurations.

## When it applies

- `capsh --print` shows `cap_sys_module`.
- The container shares the host kernel and can write to `/lib/modules`.
- The goal is a container escape to host root.

## Procedure

1. Enumerate capabilities and the kernel version.
2. Build a module that runs a command or opens a shell.
3. Copy it into the container and load it with `insmod`.
4. Verify execution in the host context.

## Commands

```bash
capsh --print
uname -r
# Build a minimal module on a compatible host
make -C /lib/modules/$(uname -r)/build M=$PWD modules
insmod ./escape.ko
# Alternative: move the module into the container and load it there
```

## Variants

- Use a module that modifies `modprobe_path`.
- Load a rootkit that hides processes and files.
- Combine it with `CAP_SYS_ADMIN` to mount the host.

## Limitations

- The container must share the kernel and allow `init_module`.
- Secure Boot or module signatures may block loading.
- The kernel version must match the available headers.

## Mitigation

- Drop `CAP_SYS_MODULE` from every container.
- Enforce seccomp and AppArmor; use user namespaces.
- Sign modules and enable Secure Boot.

## Detection

- `init_module` or `finit_module` calls from containers.
- New modules in `/proc/modules`.
- Compilers and kernel headers in production images.

## References

- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Docker — Runtime privileges](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities)
- [0xdf — MagicGardens](https://0xdf.gitlab.io/2025/02/08/htb-magicgardens.html)
