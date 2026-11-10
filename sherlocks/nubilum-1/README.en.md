---
sherlock: Nubilum-1
domain: Cloud / AWS
difficulty: Medium
platform: Hack The Box
state: Retired
evidence: CloudTrail, EC2 artefacts (CatScale), S3 copy and interview
tools: [jq, AWS CLI, Splunk, CyberChef]
tags: [dfir, cloud, aws, cloudtrail, ec2, s3, poshc2]
---

# Nubilum-1 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; no platform answers.

## Scenario

Amazon warns that one **EC2** in the account is being used for malicious purposes. The cloud administrator does not remember deploying it, but does remember seeing **more than six instances** running when logging into the console. You get the triage interview, the **CloudTrail** logs, a **CatScale** capture of the instance, a copy of the bucket and an "unusual" directory.

## Evidence

```text
CloudTrail/949622803460/CloudTrail/<region>/*.json   (~8,700 files)
catscale_ip-172-31-24-20-20230130-1628.tar.gz        (EC2 artefacts)
forela-storage/                                      (S3 bucket copy)
unusual-directory.zip                                 (directory found on the host)
interview.txt                                         (sysadmin interview)
```

## Investigation

### 1. Normalise CloudTrail

The JSON files carry `Records[]` and are split by region; merge and sort them by time first, or there is no timeline.

```bash
jq -s '[.[].Records[]] | sort_by(.eventTime)' CloudTrail/*/*.json > merged.json
jq -r '.[] | [.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress] | @tsv' merged.json | sort > timeline.tsv
```

### 2. The compromised identity

The interview states which users and roles exist; anything outside it is the attacker's. The usual pattern: an EC2 automation user allowed to create instances and key pairs.

```bash
jq -r '.[].userIdentity.arn' merged.json | sort | uniq -c | sort -rn | head
jq -r '.[] | select(.eventName|test("RunInstances|CreateKeyPair|CreateAccessKey")) | [.eventTime,.eventName,.userIdentity.arn,.sourceIPAddress] | @tsv' merged.json
```

### 3. Where the keys were

The bucket copy contains a backup script with an `access_key`/`secret_key` pair in clear text. Searching the `AKIA` prefix finds the file and its path inside the bucket.

```bash
grep -rn "AKIA" forela-storage/ | head
```

### 4. Timeline of the abuse

With the user identified, isolate its `sourceIPAddress` values: several addresses from the same range, in ascending order, distinct from legitimate traffic. They give the hours of instance and key-pair creation.

```bash
jq -r '.[] | select(.userIdentity.arn|test("<automation-user>")) | .sourceIPAddress' merged.json | sort -u
```

### 5. The implant

`unusual-directory.zip` holds the C2 framework installed on the instance: **PoshC2**. The CatScale `tar.gz` confirms it through the process list, listening ports and files in the install directory.

```bash
tar xzf catscale_*.tar.gz && ls -R | head -40
grep -rl "poshc2\|PoshC2" . | head
```

## Findings

- Entry: IAM keys of an automation user **hardcoded** in a script inside an S3 bucket.
- Abuse: creation of key pairs and extra EC2 instances from attacker IPs.
- Implant: **PoshC2** on the instance AWS reported.
- Likely persistence: keys and users created that survive instance deletion.

## Lessons

- CloudTrail is the cloud's PCAP: identity, action, time and origin per event.
- Nearly 9,000 files are handled with `jq`, not by opening them: merge, deduplicate by `eventID`, filter by `eventName`.
- The interview defines the **baseline**: without it, legitimate and added activity are indistinguishable.
- Deleting the instance does not revoke keys created earlier: rotate and audit IAM.
- A secret in a backup script is a public secret: `AWS Secrets Manager` or an instance role, never a clear-text `access_key`.
