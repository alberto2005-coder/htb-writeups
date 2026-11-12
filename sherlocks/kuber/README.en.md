---
sherlock: Kuber
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, kubernetes, yaml, secrets, container]
---

# Kuber — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation note; no literal platform answers.

## Scenario

A dump of Kubernetes resources is provided. The task is to identify how an SSH service was exposed, which secrets were readable and which pod ran a reverse shell. The case teaches reading YAML manifests as evidence: Service, ConfigMap, Secret and Pod tell the story without API server logs.

## Evidence

- `evidence/kube-system/*.yaml`, one file per resource type.
- `service.yaml`, `configmaps.yaml`, `secrets.yaml`, `pods.yaml`.
- Deployment, daemonset, job, serviceaccount and namespace manifests.
- `Secret` values encoded in base64 (not encrypted).

```bash
sha256sum evidence/kube-system/*.yaml
grep -R "kind:" evidence/kube-system | sort | uniq -c
```

## Investigation

### 1. Inventory and triage

Identify the namespace and objects that do not belong to the baseline. `kube-system` should hold control-plane components, not arbitrary workloads.

```bash
grep -nE "^(kind|  name|  namespace):" evidence/kube-system/*.yaml
```

### 2. Timeline

Manifests do not always preserve timestamps. Reconstruct the sequence through references: which Service selects which Pod, which ConfigMap/Secret it consumes and which image the Pod uses. If the dump includes `metadata.creationTimestamp`, use it as the primary source; otherwise document the limitation.

### 3. Key artifact

The Service exposes SSH externally through a `nodePort`. The `ssh-config` ConfigMap holds plaintext values; the `ssh-secret` Secret holds `USER_PASSWORD` in base64. The malicious Pod mimics `metrics-server`, uses the `alpine` image and runs `nc` against an external IP.

```bash
grep -n -B8 -A8 "nodePort" evidence/kube-system/service.yaml
grep -n -A12 "name: ssh-config" evidence/kube-system/configmaps.yaml
grep -n "USER_PASSWORD" evidence/kube-system/secrets.yaml
grep -n -E "name:|image:|nc " evidence/kube-system/pods.yaml
```

Base64 is encoding, not encryption:

```bash
echo '<BASE64_VALUE>' | base64 -d
```

The Pod name mimics the legitimate component, but its `command` has nothing to do with metrics. That mismatch between name and behaviour is the masquerading evidence.

## Findings

- The SSH service was published outside the cluster through a NodePort.
- Credentials sat in a ConfigMap and in a Secret only encoded in base64.
- The attacker created a Pod in `kube-system` with a minimal image and a reverse shell.
- The Pod was named like `metrics-server` to blend in.

## Lessons

- Do not expose SSH through a NodePort; use a bastion, VPN or `kubectl port-forward`.
- ConfigMaps are not a secret store; Secrets need RBAC, encryption at rest and an external manager.
- Alert on new Pods in `kube-system` that do not belong to a known controller.
- An admission policy restricting images and commands would have blocked the Pod.
