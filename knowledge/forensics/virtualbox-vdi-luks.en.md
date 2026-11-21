---
topic: VirtualBox — encrypted VDI and LUKS
tags: [forensics, virtualbox, vdi, luks, hashcat, credentials, moderators]
---

# VirtualBox — encrypted VDI and LUKS

**English** | [🌐 Español](virtualbox-vdi-luks.md)

## Idea

A VirtualBox VM consists of a `.vbox` configuration file and a `.vdi` disk. VirtualBox can encrypt the disk, and the guest may also have a LUKS partition. Accessing the data requires breaking or knowing both layers: the VirtualBox encryption password and the LUKS one. On Moderators, `2019.vdi` was protected by both and the resulting password worked for `sudo`.

## When it applies

- A `.vdi` and `.vbox` are accessible in a home, share or backup.
- The disk is encrypted by VirtualBox (`encryption` in the `.vbox`).
- LUKS or another disk encryption exists inside.
- Passwords are weak or reused.

## Procedure

1. Copy the `.vdi` and `.vbox` to the analysis machine.
2. Identify the encryption and extract the required material.
3. Crack the VirtualBox password with `pyvboxdie-cracker` or with the hash produced by `virtualbox2hashcat.py`.
4. Decrypt the VDI and mount or convert it.
5. Detect and open the LUKS partition.
6. Search for credentials and configuration files.

## Commands

```bash
file 2019.vdi
python3 pyvboxdie-cracker.py -v 2019-08-01.vbox -d /usr/share/wordlists/rockyou.txt
```

```bash
# After decrypting and mounting the VDI
cryptsetup luksDump /dev/loopXpY
cryptsetup luksOpen /dev/loopXpY vdi_crypt
mount /dev/mapper/vdi_crypt /mnt
```

## Variants

- `VBoxManage encryptmedium` with the known password.
- Extract the VirtualBox hash with dedicated tooling.
- Use `qemu-nbd` to mount the VDI.
- Test the LUKS passphrase locally with `cryptsetup luksOpen --test-passphrase`; Hashcat does not support LUKS2 in that version.
- Search for the password in the `.vbox`, scripts or notes.

## Limitations

- Strong passwords make cracking infeasible.
- VirtualBox encryption and LUKS are independent layers.
- The VDI may be incomplete or damaged.
- Mounting disks requires permissions and tools.
- Data may live in a snapshot or differencing disk.

## Mitigation

- Use long, unique VirtualBox and LUKS passwords.
- Do not store VMs with credentials in user homes.
- Encrypt backups and restrict access.
- Rotate credentials found in images.
- Audit access to `.vdi` and `.vbox` files.

## Detection

- Copies of `.vdi`/`.vbox` leaving the host.
- Execution of `pyvboxdie-cracker`, `hashcat` or `cryptsetup`.
- Disk images mounted on user machines.
- VM credentials used on the host.
- Access to virtual machine backups.

## References

- [0xdf — Moderators](https://0xdf.gitlab.io/2022/11/05/htb-moderators.html)
- [VirtualBox — Disk encryption](https://www.virtualbox.org/manual/ch09.html#diskencryption)
- [GitLab — pyvboxdie-cracker](https://gitlab.com/search?search=pyvboxdie-cracker)
- [Moderators writeup](../../machines/linux/moderators/README.en.md)
