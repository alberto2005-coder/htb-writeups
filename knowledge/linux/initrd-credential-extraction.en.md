---
topic: initrd — boot credential extraction
tags: [linux, initrd, cpio, credentials, privesc]
---

# initrd — boot credential extraction

**English** | [🌐 Español](initrd-credential-extraction.md)

## Concept

The initrd contains scripts and binaries that run before the real system. If readable, it can be unpacked to inspect `cryptroot`/`uinitrd`; it may contain root's password or a binary that generates it.

## When it applies

- The user is in `grub` or can read `/boot`.
- The initrd is not encrypted or signed.
- It has LUKS unlock scripts or `uinitrd`.

## Procedure

1. Locate the initrd and check its format.
2. Unpack with `zcat` and `cpio`.
3. Review `scripts/local-top/cryptroot`.
4. Run the binary or read the password.

## Commands

```bash
zcat /boot/initrd.img-<VER> | cpio -idm
./sbin/uinitrd <ARG>
su root
```

## Variants

- Initrd with `cryptsetup` and an embedded key.
- Binary deriving the key from an argument.
- `/boot` backup on another host.

## Limitations

- The initrd may be signed or encrypted.
- The binary may require the original host.
- The password may be rotated.

## Mitigation

- Restrict `/boot` and `grub` group access.
- Sign/verify initrd and use TPM.
- Keep secrets out of boot scripts.

## Detection

- Reads of `/boot/initrd*` by non-root.
- `uinitrd` execution outside boot.
- Changes to `cryptroot` scripts.

## References

- [0xdf — Unattended](https://0xdf.gitlab.io/2019/08/24/htb-unattended.html)
- [Linux — initrd](https://www.kernel.org/doc/html/latest/admin-guide/initrd.html)
- [cpio — manual](https://www.gnu.org/software/cpio/manual/)
