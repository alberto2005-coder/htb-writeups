---
machine: Giveback
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, kubernetes, runc, privesc]
---

# Giveback — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress runs GiveWP, vulnerable to CVE-2024-5932; a POP chain yields a shell in the Kubernetes pod. The `legacy-internet-cms` pod runs PHP 8.1, vulnerable to CVE-2024-4577, allowing root inside the container. The service-account token and Kubernetes API lead to secrets and SSH as `babywyrm`; on the host, runc CVE-2024-21626 escapes to root.

## Recon

```bash
nmap -Pn -sCV -p22,80,30686 <IP>
```

- `22` SSH, `80` WordPress and `30686` a web API.
- The main site is a donation site running WordPress.
- The API exposes internal endpoints and a Kubernetes environment.

## Enumeration

- `wpscan` identifies the GiveWP plugin vulnerable to CVE-2024-5932.
- The plugin allows a POP chain that writes a PHP file.
- Pods use a service account with access to secrets.

## Foothold

Send the CVE-2024-5932 payload and get execution in the WordPress pod; the webshell enumerates the cluster and finds the `legacy-internet-cms` pod.

```bash
curl -s 'http://<IP>/wp-admin/admin-ajax.php' --data 'action=give_process_donation&give-form-id=1&...'
```

## Lateral movement

The legacy pod runs PHP-CGI 8.1, vulnerable to CVE-2024-4577. Exploit it for root in the container and read the service-account token; use it to list secrets and recover `babywyrm` SSH credentials.

```bash
kubectl --token=<TOKEN> --server=https://kubernetes.default.svc get secrets -A
```

## Privilege escalation

`babywyrm` can run containers on the host. Use runc CVE-2024-21626 to escape, write a key to `/root/.ssh/authorized_keys` and log in as root.

```bash
docker run --rm -it -v /:/host <IMAGE> /bin/sh
```

## Evidence

- GiveWP CVE-2024-5932 and webshell in the pod.
- PHP-CGI CVE-2024-4577 and root in the container.
- Service-account token and Kubernetes secrets.
- runc CVE-2024-21626 and host root.

## Lessons learned

- A WordPress plugin can be the door to an entire cluster.
- An old pod with vulnerable PHP-CGI breaks container isolation.
- Service-account tokens must have least privilege.

## Mitigation and detection

- Update GiveWP and PHP; remove PHP-CGI.
- Enforce strict RBAC and rotate service-account tokens.
- Update runc and avoid mounting the host filesystem.

## References

- [0xdf — Giveback](https://0xdf.gitlab.io/2026/02/21/htb-giveback.html)
- [IppSec — Giveback](https://www.youtube.com/watch?v=wNKWDKleH04)
- [Hack The Box — Giveback](https://app.hackthebox.com/machines/giveback)
