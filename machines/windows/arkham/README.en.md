---
machine: Arkham
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, luks, jsf, deserialization, winrm]
---

# Arkham — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An SMB share contains a ZIP with a LUKS image and a note. The image is decrypted and reveals the Tomcat/JSF configuration, including the ViewState key. Java deserialization in `userSubscribe.faces` gives a shell as `alfred`. An Outlook OST stores `batman` credentials, and WinRM plus a UAC bypass lead to Administrator.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
80/tcp    http    Microsoft IIS 10.0
135/tcp   msrpc
139/tcp   netbios-ssn
445/tcp   smb
8080/tcp  http    Apache Tomcat / JSF
49666/tcp msrpc
49667/tcp msrpc
```

## Enumeration

- The `batshare` share is accessible without credentials and contains `appserver.zip`.
- The ZIP includes `IMPORTANT.txt` and `backup.img`, a LUKS image.
- The site on 8080 uses JSF with `*.faces` and server-side state.
- SMB and host enumeration suggest a Windows environment running Tomcat.

## Foothold

The LUKS password is recovered with a wordlist and `bruteforce-luks`. Mounting it exposes Tomcat files and `web.xml.bak`, which leaks `org.apache.myfaces.SECRET` and the MAC algorithm.

That key builds a malicious ViewState: a `ysoserial` `CommonsCollections5` payload is serialized, DES-ECB encrypted, HMAC-SHA1 signed and sent in the hidden field of `userSubscribe.faces`.

```bash
bruteforce-luks -f wordlist.txt backup.img
mount /dev/mapper/<MAPPER> /mnt
python3 jsf_payload.py '<COMMAND>'
```

## Lateral movement

The initial shell is `alfred`. Their desktop holds `backup.zip` with an Outlook OST. Messages are extracted and `arkham\batman` credentials are recovered.

`New-PSSession` or WinRM opens a session as `batman`, who belongs to an administrative group.

```powershell
New-PSSession -ComputerName . -Credential $cred
Enter-PSSession -Session $s
```

## Privilege escalation

The `batman` session allows commands with elevated privileges, but the process still carries a filtered token. A UAC bypass based on an auto-elevating binary launches a shell with Administrator's full token.

```powershell
whoami /groups
# choose a UAC bypass compatible with the Windows version
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- A disk backup can contain plaintext application secrets.
- The ViewState key turns JSF into a deserialization surface.
- Outlook OST files are a common credential source.
- Being in Administrators does not remove UAC filtering.

## Mitigations and detection

- Encrypt backups and restrict access to sensitive shares.
- Rotate JSF keys and keep configuration out of accessible backups.
- Disable anonymous SMB access and audit shares.
- Set UAC to maximum and review auto-elevating binaries.

## References

- [0xdf — Arkham](https://0xdf.gitlab.io/2019/08/10/htb-arkham.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+arkham)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+arkham+writeup)
