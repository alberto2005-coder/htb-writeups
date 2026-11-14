---
topic: FTP enumeration
tags: [general, ftp, enumeration, anonymous, upload, vsftpd]
---

# FTP enumeration

**English** | [🇪🇸 Español](ftp-enumeration.md)

## Concept

FTP exposes files and often allows anonymous writes or weak credentials. Enumeration looks for vulnerable versions, accessible directories, configuration files and the ability to upload a webshell or script.

## When it applies

- Port 21 open.
- A `vsftpd`, `ProFTPD` or `FileZilla Server` banner.
- Anonymous or guest access.
- An upload directory inside a webroot.

## Procedure

1. Identify the service and version.
2. Test anonymous access.
3. List directories and download relevant files.
4. Look for credentials, backups and keys.
5. Test writes and execution from the webroot.

```bash
ftp <HOST>
# user: anonymous, empty password
wget -m --no-passive ftp://anonymous:anonymous@<HOST>/
curl -s ftp://anonymous:anonymous@<HOST>/ --list-only
```

## Variants

- `vsftpd 2.3.4` with a known backdoor.
- FTP over TLS with a weak certificate.
- Uploading `.php`, `.aspx` or `.war`.
- The same directory mounted over NFS or SMB.

## Limitations

- Anonymous access may be disabled.
- A firewall may allow control but not passive data.
- The webroot may not be the FTP directory.
- Uploads may require special permissions.

## Mitigation and detection

- Disable anonymous FTP and use SFTP.
- Restrict writes and separate the webroot.
- Update the server and limit exposure.
- Alert on anonymous logins, bulk transfers and executable uploads.

## References

- <https://www.rfc-editor.org/rfc/rfc959>
- <https://attack.mitre.org/techniques/T1021/002/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-ftp/index.html>
