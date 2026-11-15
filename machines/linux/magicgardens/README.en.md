---
machine: MagicGardens
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, django, xss, ipv6, docker, capabilities, kernel-module]
---

# MagicGardens — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The shop allows manipulating the purchase flow to enable a premium feature; an XSS in the QR leads to the Django panel and SSH. An IPv6 buffer overflow in `harvest` yields another user, the Docker registry leaks the Django secret, and `CAP_SYS_MODULE` allows loading a module and escaping to the host.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443,5000 <IP>
ffuf -u http://magicgardens.htb -H "Host: FUZZ.magicgardens.htb" -w subdomains.txt
# XSS in the QR and Django panel
curl -s "http://magicgardens.htb/qr?data=<PAYLOAD>"
# After the pivot
capsh --print
ls -la /lib/modules/$(uname -r)
insmod /tmp/rootkit.ko
```

## Enumeration

- Django shop with cart, coupons and QR generation.
- `harvest` service processing IPv6 packets.
- Internal Docker registry and containers with broad capabilities.

## Initial access

Alter the purchase flow to obtain the premium feature and inject XSS into the QR content. The admin bot visits the link and allows taking over the Django panel; from there, reach an SSH key.

## Privilege escalation

The `harvest` binary has an IPv6 handling overflow that gives another user. The Docker registry image contains the Django secret and allows deserialization as root in the container; `CAP_SYS_MODULE` enables loading a module and becoming root on the host.

## Evidence

- Manipulated premium purchase and XSS callback.
- Django panel access and SSH.
- `capsh --print` showing `cap_sys_module` and a loaded module.

## Lessons learned

- Premium business logic may be validated only on the client.
- A C network parser remains a memory surface.
- A broad capability in a container can equal host root.

## Mitigation and detection

- Validate prices and privileges server-side; sanitize the QR.
- Build with mitigations and review IPv6 parsers.
- Drop `CAP_SYS_MODULE` and enforce seccomp/AppArmor.

## References

- [0xdf — MagicGardens](https://0xdf.gitlab.io/2025/02/08/htb-magicgardens.html)
- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Hack The Box — MagicGardens](https://app.hackthebox.com/machines/magicgardens)
