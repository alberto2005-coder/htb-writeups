---
machine: Keeper
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, request-tracker, default-creds, keepass, cve-2023-32784, ssh]
---

# Keeper — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Request Tracker 4.4.4 on `tickets.keeper.htb` keeps the default credentials. A ticket contains `lnorgaard`'s initial password, valid over SSH. Their home holds a KeePass memory dump and the `.kdbx` database; CVE-2023-32784 recovers the master password and inside is root's private key.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

Port 80 redirects to `tickets.keeper.htb`. Add it to hosts:

```bash
echo '<IP> tickets.keeper.htb keeper.htb' | sudo tee -a /etc/hosts
```

The application is Request Tracker 4.4.4.

## Initial access

Try RT's documented default credentials (`root` and the default password). Under `Admin → Users` a ticket/comment holds `lnorgaard`'s initial password. Reuse it over SSH:

```bash
ssh lnorgaard@<IP>
```

## Privilege escalation

`/home/lnorgaard` contains a ZIP with `KeePassDumpFull.dmp` and `passcodes.kdbx`. CVE-2023-32784 recovers the master password from the dump:

```bash
python3 keepass_dump.py KeePassDumpFull.dmp
kpcli --kdb passcodes.kdbx
```

The database holds root's PuTTY private key. Convert and use it:

```bash
puttygen root.ppk -O private-openssh -o root.id_rsa
chmod 600 root.id_rsa
ssh -i root.id_rsa root@<IP>
```

## Evidence

- RT login and ticket with password redacted.
- `KeePassDumpFull.dmp` and `passcodes.kdbx`.
- Recovered master password and root key redacted.

## Lessons learned

- RT default credentials still appear in production.
- Tickets may hold cleartext secrets.
- KeePass memory dumps leak the master password.
- A root key in a shared vault completes the chain.

## Mitigation and detection

- Change default credentials and enforce MFA.
- Never store passwords in tickets/comments.
- Update KeePass and restrict process dumps.
- Detect access to `KeePassDumpFull.dmp` and `kpcli`.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2023-32784>
- <https://www.hackthebox.com/machines/keeper>
- <https://bestpractical.com/request-tracker>
