---
sherlock: Heartbreaker-Denouement
domain: Cloud
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [cloud, aws, cloudtrail, ssrf, imds, rds, exfiltration]
---

# Heartbreaker-Denouement — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no literal platform answers.

## Scenario

A customer reports their data being sold on a darknet market. The only initial lead is a compromised AWS credential. The bundle contains a UAC collection from the web server and CloudTrail logs: determine whether exfiltration happened and rebuild the chain.

The investigation ends far from the server: the actor never touches the host again, moving two RDS databases into their own account through the AWS API.

## Evidence

```text
uac                      web server tarball
├── access.log           Apache requests and status codes
├── error.log            application messages (including user input)
├── .bash_history
├── .mysql_history       MySQL client queries
└── webroot/             application code

cloudtrail/              ~9,000 gzipped JSON files, one per event
```

```bash
tar xzf uac -C work/tar
gzip -dc cloudtrail/*.json.gz > work/ct/all.jsonl     # or merge with Python
```

## Investigation

### 1. Recon and initial access

`access.log` shows an external IP firing hundreds of dictionary paths, almost all `404`: **wordlist scanning** (T1595.003). The noise breaks when one path returns `301` and reveals the real application.

In `error.log`, `Input:` lines show the page passing user input to `file_get_contents`. It first reads local files with `file:///`, then targets `http://169.254.169.254`, the instance metadata service. That is **SSRF** (T1190) reaching a destination only routable from the VM.

```bash
grep -c ' 404 ' access.log
grep -vE ' 404 ' access.log | grep -E ' 30[0-9] '
grep 'Input:' error.log | head
grep -r '169.254.169.254' error.log access.log
```

### 2. Credentials and discovery

The SSRF returns the instance role credentials. In parallel, a leaked IAM user key is used from the same IPs. With CloudTrail merged into JSONL, the pattern is:

```bash
python3 summarize_ct.py work/ct/all.jsonl --user devops-ash --by eventName
python3 summarize_ct.py work/ct/all.jsonl --user devops-ash --success --by awsRegion
```

- `GetCallerIdentity` is AWS's "whoami": no permissions needed, confirms who the keys belong to (T1033).
- `DescribeInstances` lists instances and their public IPs, consistent with earlier recon (T1580).
- The IAM user's calls succeed in **two** regions; counting every region from the attacker IPs mixes in role credentials and gives a larger number.

### 3. Collection and exfiltration

`CreateDBSnapshot` against two production databases (T1578.001), with the date in the snapshot name. Then `ModifyDBSnapshotAttribute` adds a foreign account to `valuesToAdd`: the snapshot is shared with the actor's account and the copy happens inside AWS (T1537).

```bash
python3 summarize_ct.py work/ct/all.jsonl --event CreateDBSnapshot \
  --field requestParameters.dBSnapshotIdentifier
python3 summarize_ct.py work/ct/all.jsonl --event ModifyDBSnapshotAttribute \
  --field requestParameters.valuesToAdd
```

Failures matter too: hundreds of `AccessDenied` from the actor IPs trace the permission enumeration.

## Conclusions

- Entry was an SSRF in a PHP page; the metadata service handed over role credentials.
- The leaked IAM key and the instance role were used from outside; CloudTrail separates them by `userIdentity.arn`.
- Exfiltration needs no server access: RDS snapshots shared with another account.
- Key defences: block schemes and hosts in server-side fetches, enforce **IMDSv2** with hop limit 1, rotate leaked keys and alert on `ModifyDBSnapshotAttribute` targeting external accounts.

## References

- <https://labs.hackthebox.com/sherlocks/heartbreaker-denouement>
- <https://inksec.io/blue-team/sherlocks/heartbreaker-denouement>
- <https://www.moamenbasel.com/htb-writeups/sherlocks>
- <https://attack.mitre.org/techniques/T1537/>
