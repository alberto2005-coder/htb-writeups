---
machine: PikaTwoo
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, openstack, apisix, kubernetes, cr8escape]
---

# PikaTwoo — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The API has SQLi and leaks a valid email. An old APISIX bypasses the `/private` block with `//`, resets the password and authenticates. A ModSecurity rule is then bypassed for LFI and RCE in the API pod. The Kubernetes token leaks the APISIX key, which gives RCE in its pod; credentials in a file provide SSH and `cr8escape` (CVE-2022-0811) gives root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh
80/tcp    http    nginx
443/tcp   https   APISIX 2.10.1
4369/tcp  epmd
5000/tcp  keystone
5672/tcp  amqp
8080/tcp  swift
25672/tcp rabbitmq
35357/tcp keystone admin
```

## Enumeration

- The Android APK and Pokedex API are advertised on the site.
- The API has SQLi; a registered email is leaked.
- APISIX 2.10.1 blocks `/private` with `uri-block`.
- The API pod mounts a Kubernetes service-account token.

## Foothold

API SQLi is exploited to obtain a valid email. With APISIX 2.10.1, `//private/` bypasses the rule blocking `/private`; private documentation is reached and the email password is reset.

After authentication, a ModSecurity/CRS rule is bypassed for LFI. Nginx temporary files are abused to write and execute a reverse shell in the pod.

```bash
curl -k https://<IP>/%70rivate/login
curl -k -X POST https://<IP>/%70rivate/login -d 'email=<EMAIL>&password=<PASSWORD>'
```

## Lateral movement

The API pod has a service-account token. The Kubernetes API is queried and namespace secrets are read, including the APISIX admin key.

With that key, `CVE-2022-24112` in `batch-requests` creates a route with `filter_func` and runs commands in the APISIX pod. A configuration file holds `andrew` credentials, providing SSH to the host.

```bash
curl --cacert ca.crt -H "Authorization: Bearer $TOKEN"   https://kubernetes.default.svc/api/v1/namespaces/$NS/secrets
```

## Privilege escalation

`andrew` can use `kubectl` with another user's config, but cannot list pods. The CRI-O version is vulnerable to `cr8escape` (CVE-2022-0811): a pod injects `kernel.core_pattern` and a crash runs a host script as root.

```bash
kubectl --kubeconfig /home/<USER>/.kube/config get pods
# create a pod with the malicious sysctl and trigger SIGSEGV
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- SQLi can be the first step in a complex cloud chain.
- Normalising the URL before block rules is critical.
- Service-account tokens must follow least privilege.
- Unpatched CRI-O allows container escape through `core_pattern`.

## Mitigations and detection

- Parameterise SQL and validate API input.
- Update APISIX and normalise paths before `uri-block`.
- Restrict service-account secrets and RBAC.
- Update CRI-O and block dangerous sysctls.

## References

- [0xdf — PikaTwoo](https://0xdf.gitlab.io/2023/09/09/htb-pikatwoo.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+pikatwoo)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+pikatwoo+writeup)
