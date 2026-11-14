---
sherlock: Cookie Consumption
category: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, kubernetes, secrets, service-account, cloud]
---

# Cookie Consumption — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal answers or real data.

## Scenario

Santa's cookie scheduler runs on Kubernetes. A namespace export is provided and an attacker may have created resources, read secrets or changed the cronjob. Reconstruct the activity.

## Evidence

- YAML/JSON namespace export.
- Pod, deployment, service account, secret and cronjob manifests.
- No live cluster.

```bash
kubectl get all,secrets,serviceaccounts -n <NAMESPACE> -o yaml
```

## Investigation

### 1. Inventory and triage

List objects and look for anomalous names and dates. `serviceaccounts` with broad permissions and mounted `secrets` are likely targets.

```bash
yq '.items[] | [.kind,.metadata.name,.metadata.creationTimestamp]' dump.yaml
```

### 2. Timeline

Sort by `creationTimestamp` and compare with the legitimate deployment. A new pod mounting another service's token, or a cronjob running an external image, stands out.

### 3. Key artefact

The `serviceaccount` and its `RoleBinding` show the scope. The `secret` shows which credentials were exposed; the `cronjob` reveals persistence.

```bash
yq '.items[] | select(.kind=="CronJob") | .spec.jobTemplate.spec.template.spec.containers[].image' dump.yaml
```

## Conclusions

- The attacker created or modified resources in the namespace.
- A service token allowed secret reads.
- The malicious cronjob or pod provided persistence.
- Credential rotation is mandatory.

## Lessons

- Kubernetes requires reviewing RBAC and mounted tokens.
- A static dump is enough to reconstruct objects.
- Application secrets do not belong in environment variables.

## References

- <https://www.hackthebox.com/sherlocks/Cookie%20Consumption>
- <https://kubernetes.io/docs/concepts/security/service-accounts/>
- <https://attack.mitre.org/techniques/T1552/007/>
