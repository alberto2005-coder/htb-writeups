---
topic: ManageEngine ServiceDesk Plus — XXE and LFI
tags: [windows, manageengine, servicedesk, xxe, lfi, privesc]
---

# ManageEngine ServiceDesk Plus — XXE and LFI

**English** | [🌐 Español](manageengine-servicedesk-xxe.md)

## Concept

ServiceDesk Plus with default or guest accounts exposes APIs and files. CVE-2017-9362 allows XXE file reads, and CVE-2017-11511 allows LFI; both can leak credentials and reach the database or SYSTEM.

## When it applies

- SDP panel on 8080 with guest or default account.
- Version predates the 2017 patches.
- WinRM/SMB is available for credential reuse.

## Procedure

1. Try default and guest accounts.
2. Send XML with an external entity to the API.
3. Read configuration and credential files.
4. Use LFI to download panel files.

## Commands

```bash
# XML with <!ENTITY xxe SYSTEM "file:///C:/temp/it_logins.txt">
python3 mesep_xxe.py <IP> "C:\temp\Password Audit\it_logins.txt"
```

## Variants

- XXE through SOAP or REST.
- LFI with paths relative to four directories.
- PostgreSQL trigger to SYSTEM.

## Limitations

- Guest may be disabled.
- XXE may require authentication.
- Sensitive files may use EFS.

## Mitigation

- Disable guest and change defaults.
- Update SDP and disable external entities.
- Restrict WinRM and protect EFS.

## Detection

- XML with `SYSTEM` or `ENTITY`.
- Access to `it_logins.txt` or backups.
- Service accounts used from new IPs.

## References

- [0xdf — Helpline](https://0xdf.gitlab.io/2019/08/17/htb-helpline.html)
- [NVD — CVE-2017-9362](https://nvd.nist.gov/vuln/detail/CVE-2017-9362)
- [NVD — CVE-2017-11511](https://nvd.nist.gov/vuln/detail/CVE-2017-11511)
