---
sherlock: Nubilum-1
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
evidence: CloudTrail logs, EC2 artifacts and an S3 copy
tools: [jq, AWS CLI, CyberChef, Elastic]
---

# Nubilum-1 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

Amazon warns that an **EC2** instance in the environment is being used maliciously. The cloud admin recalls seeing more instances than he deployed. You get the triage interview, **CloudTrail** logs and a capture from the compromised instance.

## Evidence

- `CloudTrail/` with the account's activity JSON.
- `catscale_*.tar.gz` with artifacts collected from the instance.
- `forela-storage/` (bucket copy), `unusual-directory.zip` and `interview.txt`.

## Method

1. **Normalise** events and keep write calls.

```bash
jq -r '[.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress]|@tsv' CloudTrail/*.json | sort | head
```

2. **Baseline**: which users and roles create resources (`RunInstances`, `CreateKeyPair`, `CreateUser`, `AttachUserPolicy`). Anything that contradicts the interview belongs to the attacker.

3. **Source IP** and time window: group by `sourceIPAddress`, count actions per hour.

4. **Instance**: the CatScale archive shows processes, connections and files; `unusual-directory.zip` usually holds the **implant**.

5. **Persistence**: check for newly created access keys, users or policies that survive instance deletion.

## What it teaches

- CloudTrail is the cloud's "PCAP": who, what, when and from where.
- Cloud abuse starts by creating resources (mining, C2) with stolen credentials.
- The admin interview is evidence: it defines the baseline.
- Deleting an instance does not revoke keys created before it.

## Pitfalls

- **Volume**: filter by `eventName` and `errorCode` before reading.
- **Roles versus users**: the effective identity may be an assumed role; follow `sessionIssuer`.
- **Time zones**: CloudTrail is UTC; the interview is not.
