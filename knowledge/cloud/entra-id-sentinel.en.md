---
topic: Entra ID and Sentinel: sign-ins, audit and KQL
tags: [cloud, azure, entra-id, sentinel, kql, identity, dfir]
---

# Entra ID and Sentinel: sign-ins, audit and KQL

**English** | [🇪🇸 Español](entra-id-sentinel.md)

> Reusable note. No tenant-specific data.

## Idea

Microsoft Entra ID (formerly Azure AD) produces two log streams that answer almost any identity investigation: **sign-ins** and **directory audit**. When the tenant exports diagnostics to a Log Analytics workspace, Sentinel queries them as `SigninLogs` and `AuditLogs`; the rest is KQL and context.

The key difference: `SigninLogs` says *who tried to sign in and what happened*; `AuditLogs` says *what changed in the directory*. A compromise usually needs both.

## Tables and columns

### `SigninLogs`

| Column | Use |
|---|---|
| `TimeGenerated` | Timeline (UTC) |
| `UserPrincipalName` | Identity signing in |
| `ResultType` | Error code; `0` means success |
| `ResultDescription` | Failure text |
| `IPAddress` | Request source |
| `Location` / `LocationDetails` | Country (two letters) and city-level detail |
| `AppDisplayName` / `AppId` | Target application |
| `DeviceDetail` / `UserAgent` | Device and client |
| `RiskLevelDuringSignIn` / `RiskLevelAggregated` | Identity Protection risk |
| `AlternateSignInName` | Alternate identifier (phone, proxyAddress…) |

`AADNonInteractiveUserSignInLogs` covers non-interactive sign-ins (service tokens, refresh). `AADRiskyUsers` and `AADUserRiskEvents` require Identity Protection.

### `AuditLogs`

| Column | Use |
|---|---|
| `TimeGenerated` | Timeline |
| `OperationName` | Action ("Add member to role.", "Consent to application."…) |
| `InitiatedBy` | Who ran it (user, app, IP) |
| `TargetResources` | Affected object |
| `Result` | Success or failure |

## Queries

```kusto
// grouped failures: brute force or password spray
SigninLogs
| where TimeGenerated > ago(7d)
| where ResultType != "0"
| summarize Failures = count(), First = min(TimeGenerated), Last = max(TimeGenerated)
    by UserPrincipalName, IPAddress, ResultType
| order by Failures desc

// distinct successful locations: possible impossible travel
SigninLogs
| where TimeGenerated > ago(7d) and ResultType == "0"
| summarize Countries = dcount(Location), Locations = make_set(Location, 10) by UserPrincipalName
| where Countries > 1

// success after many failures from the same IP
let failures = SigninLogs
| where TimeGenerated > ago(24h) and ResultType != "0"
| summarize Failures = count() by IPAddress, UserPrincipalName;
SigninLogs
| where TimeGenerated > ago(24h) and ResultType == "0"
| join kind=inner failures on IPAddress, UserPrincipalName
| where Failures >= 10
| project TimeGenerated, UserPrincipalName, IPAddress, AppDisplayName, Failures

// sensitive directory changes
AuditLogs
| where TimeGenerated > ago(7d)
| where OperationName in ("Add member to role.", "Consent to application.",
    "Add service principal credentials.", "Update user.", "Reset password (by admin)")
| project TimeGenerated, OperationName, InitiatedBy, TargetResources, Result
```

## Useful error codes

| Code | Meaning |
|---:|---|
| `0` | Success |
| `50126` | Invalid username or password |
| `50074` | MFA required |
| `50076` | MFA not satisfied |
| `50105` | User not assigned to the application |
| `53003` | Blocked by conditional access |
| `65001` | Consent not granted |

The full list lives at `https://login.microsoftonline.com/error`; do not copy it wholesale.

## Limits that change the investigation

- **Licensing**: conditional access needs P1; risk fields need P2. Without P2 they appear as `hidden` or empty.
- **Retention**: Log Analytics expires; for older incidents only exported data in Sentinel or storage may remain.
- **Coverage**: Entra ID diagnostics decide what is sent. A tenant without the `SigninLogs` connector has nothing to query.
- **Time zone**: `TimeGenerated` is UTC; questions usually ask for UTC.

## Detection

- Spikes of `50126` from one IP across many accounts: password spray.
- Success from a new country right after failures: valid credentials obtained.
- Repeated `50076` followed by success: MFA bypass attempt.
- New app credentials or consents: persistence.
- Privileged roles added outside a change window: privilege escalation.

MITRE ATT&CK: T1110 (Brute Force), T1078.004 (Cloud Accounts), T1556 (Modify Authentication Process), T1098.001 (Additional Cloud Credentials).

## References

- <https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs>
- <https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/auditlogs>
- <https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins>
- <https://learn.microsoft.com/en-us/azure/sentinel/connect-azure-active-directory>
