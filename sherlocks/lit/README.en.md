---
sherlock: Lit
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, rdp, brute-force, evtx, logon]
---

# Lit — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

A Windows server suffers RDP brute force. Events 4625/4624/4776 and `Security.evtx` are analysed to identify the source, attempted accounts and the successful logon.

## Scenario

The security team receives alerts about multiple authentication failures on a host. The security log is provided to determine whether access occurred and from where.

## Artefacts

- `Security.evtx`.
- `Microsoft-Windows-TerminalServices-LocalSessionManager/Operational.evtx`.
- `Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational.evtx`.
- Firewall and network logs.

## Methodology

1. Filter 4625 by `Logon Type 3/10` and group by IP and account.
2. Identify the brute-force pattern and the first successful 4624.
3. Review 4776/4648 for NTLM/explicit authentication.
4. Confirm the RDP session with TerminalServices logs.
5. Document the compromised account and source.

```bash
EvtxECmd.exe -f Security.evtx --csv C:\\Evidence\\out
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625}
```

## Sample questions

- From which IP did the brute force originate?
- Which accounts were tried?
- Was there a successful login? When?
- Which logon type was used?
- Was a persistent RDP session created?

## Tools

`EvtxECmd`, `Timeline Explorer`, `Event Viewer`, `RDP log parser`.

## Evidence and redaction

Screenshots of events are kept with IPs, users and domains redacted.

## Lessons learned

- A single 4625 is not an attack; the pattern is.
- 4624 with Logon Type 10 confirms RDP.
- TerminalServices logs complement Security.
- The first success marks the investigation start.

## Detection

- Alert on many 4625 followed by 4624.
- Limit exposed RDP and enforce MFA.
- Block IPs after a failure threshold.
- Monitor valid accounts used from new locations.

## References

- <https://app.hackthebox.com/sherlocks/Lit>
- <https://attack.mitre.org/techniques/T1110/001/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4625>
