---
sherlock: Liberty
domain: DFIR
difficulty: Medium
platform: Hack The Box
evidence: Windows server triage with $MFT, EVTX, registry and profiles
tools: [EvtxECmd, MFTECmd, Registry Explorer, Timeline Explorer]
state: Active
tags: [dfir, windows, rdp, ntlm-theft, backdoor, powershell-web-access, t1021.001]
---

# Liberty — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Active. Investigation notes; no platform answers.

## Scenario

A consultancy's file server starts sending odd internal emails and accepting connections nobody recognises. The response team receives a host triage: `$MFT`, event logs, registry hives and user profiles.

## Evidence

- System volume `$MFT`.
- `Windows\System32\winevt\logs\*.evtx` (Security, System, PowerShell/Operational).
- Registry hives, including each profile's `UsrClass.dat`.
- User profiles (desktop, downloads, browser).

```bash
sha256sum "$MFT" Security.evtx SYSTEM
```

## Investigation

### 1. Inventory and triage

Order is logon → execution → persistence. Security first: it gives the who and the when; then `$MFT` and the registry supply the objects.

```bash
EvtxECmd.exe -f Security.evtx --csv out --csvf security.csv
```

Security shows **five 4625** in a few minutes from the same IP and, right after, a **4624** for `v.hunter`: a password spray that hit. Later the same day, a **4624 with Logon Type 10** (RDP) at **2025-06-11 14:44:48 UTC**.

### 2. Timeline

With RDP established, the attacker reconnoitres the host and creates a new share. Shares live in the registry:

```text
HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Shares
```

Two entries stand out: the legitimate `Proposal` share (permissions 9) and **`ProjectArk`**, pointing at `C:\ProjectArk`, which did not exist before the incident.

`$MFT` explains how credentials were stolen before RDP: a `Proposal.url` file pointing at `http://argonaut.ark/proposal.html` with a UNC path of the form:

```text
\\192.168.189.129\%USERNAME%.icon
```

A `.url` with a UNC icon makes Explorer authenticate to the attacker and hand over the **Net-NTLMv2** hash, cracked offline. That is the real origin of `v.hunter`'s password.

The *shellbags* (`UsrClass.dat`) of `k.texus` show browsing through `C:\ProjectArk`, and the registry records 7-Zip being used on `arkproj.zip`: the attacker packaged what they found.

### 3. Key artifact

Persistence lives in the PowerShell history and the feature's operational log:

```text
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
```

```powershell
Install-WindowsFeature -Name WindowsPowerShellWebAccess -IncludeManagementTools
```

The session is recorded in `Microsoft-Windows-PowerShellWebAccess%4Operational.evtx`:

```text
LIBERYSV08\t.minami.250611.075455   14:54:55 -> 14:55:40
```

In other words: the attacker enabled **PowerShell Web Access** as a backdoor, with a 45-second session to validate it.

## Findings

- Access via password spray and RDP with a valid account; no escalation was needed to move around.
- Credentials were harvested earlier with a `.url` pointing an icon at the attacker's UNC share (Net-NTLMv2 theft).
- Exfiltration through 7-Zip of a hand-made share (`ProjectArk`) and persistence via PowerShell Web Access.

## Lessons

- A `.url` on a proposals share is credential phishing without email: the vector is Explorer, not the browser.
- The spray leaves a clear pattern (several 4625 and one 4624 from the same IP); without correlation it goes unnoticed.
- `LanmanServer\Shares` is the source for detecting hand-made shares; no agent required.
- Enabling an IIS feature leaves a trail in the operational log with username and session.

## Mitigations and detection

- Block outbound SMB/NTLM authentication to the Internet and disable UNC icons in shares (equivalent GPO).
- Strong passwords and lockout after few attempts for service and human accounts; MFA on RDP.
- Monitor 4741/4738 and share creation (5142/5143) outside change windows.
- Detection: burst 4625 followed by 4624 from the same origin, Logon Type 10 from unusual IPs, `Install-WindowsFeature` with PowerShellWebAccess, and sessions in the `%4Operational` log.

MITRE: T1110.003 (password spraying), T1021.001 (RDP), T1187 (forced authentication), T1133 (external remote services), T1059.001 (PowerShell).

## References

- <https://bakosecurity.com/blog/liberty-htb-writeup>
- <https://inksec.io/blue-team/sherlocks/liberty/>
- <https://attack.mitre.org/techniques/T1187/>
- <https://learn.microsoft.com/en-us/powershell/module/microsoft.windows.servermanager/install-windowsfeature>
