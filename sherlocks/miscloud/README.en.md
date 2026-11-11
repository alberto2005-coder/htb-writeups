---
sherlock: MisCloud
domain: Cloud
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [cloud, gcp, gitea, pcap, audit-logs, service-account]
---

# MisCloud — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal platform answers.

## Scenario

A company migrates from WordPress to Google Cloud with a self-hosted Gitea. Days later, customer data shows up encrypted and outside the organisation. The package holds the VPC capture and the GCP audit logs; the job is to reconstruct the access, the pivot and the exfiltration.

## Evidence

```text
miscloud/VPCNetwork_Traffic.pcap        internal VPC traffic
miscloud/GCloud_Logs.json               Cloud Audit logs
miscloud/inventory.json                 VM and bucket inventory
```

```bash
sha256sum *                             # record before analysing
jq '.[0]' GCloud_Logs.json | head -40
```

## Investigation

### 1. Inventory and triage

Open the capture first with conversation statistics to find the chattiest host and the internal services. In parallel, `jq` over the audit logs lists the invoked methods and the identities calling them.

```bash
tshark -r VPCNetwork_Traffic.pcap -q -z conv,tcp | head -20
jq -r '.[].protoPayload.methodName' GCloud_Logs.json | sort | uniq -c | sort -rn | head
```

### 2. Timeline

The peak matches HTTP POSTs to `/git/post-receive` on the internal Gitea: a repository hook runs whatever arrives. From there the attacker downloads and runs a base64 bash script, and starts using the `compute@developer.gserviceaccount.com` service account to read the data bucket.

Order: access to the Gitea panel, creation or abuse of the hook, command execution, creation of an encrypted file and upload over HTTP.

### 3. Key artefact

The `post-receive` hook is what turns a repository into remote execution. In the audit logs, the service account's `storage.objects.get` calls from an IP that is not the documented VM prove the pivot. The capture keeps the POST with the script and the response carrying the encrypted file.

```bash
jq -r '.[] | select(.protoPayload.authenticationInfo.principalEmail|test("compute@developer")) | [.timestamp, .protoPayload.methodName] | @tsv' GCloud_Logs.json | head
```

## Conclusions

- Entry: abuse of an internet-exposed Gitea and its `post-receive` hook to run commands.
- Pivot: Compute Engine's default service account, with permissions on Cloud Storage.
- Exfiltration: customer data encrypted with a custom script and uploaded over HTTP.
- IOCs: hook path, attacker user-agent and IP, and the service account used off the VM.
- Persistence: the repository hook itself.

## Lessons

- A Gitea reachable from the internet with hooks enabled is code execution, not just a repository.
- The default service account usually has more permissions than needed; its use from another IP is a strong signal.
- GCP audit logs give identity and method; the capture gives content. Neither is enough alone.
- Mitigation: remove the default service account from VMs, apply least privilege on buckets and restrict Gitea behind a VPN.
- Detection: mass `storage.objects.get`, service-account calls from external IPs and `post-receive` requests with long bodies.
- What is missing: load-balancer logs to see the earlier scan and the real source.

MITRE: T1190 (exploit public-facing application), T1059.004 (Unix shell), T1078.004 (cloud accounts), T1530 (data from cloud storage), T1567.002 (exfiltration to cloud storage).
