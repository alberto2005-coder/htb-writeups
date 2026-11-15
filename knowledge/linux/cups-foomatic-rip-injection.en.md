---
topic: CUPS — injection in Foomatic-RIP
tags: [linux, cups, ipp, foomatic, command-injection]
---

# CUPS — injection in Foomatic-RIP

**English** | [🌐 Español](cups-foomatic-rip-injection.md)

## Concept

CUPS creates printers with attributes such as `cupsFilter` or the model name. When printing, Foomatic-RIP builds a command line from those values. If unvalidated, an attacker-controlled attribute executes commands as the spooler user, usually `lp`.

## When it applies

- CUPS administration on `631` is reachable.
- A printer can be registered or its attributes modified.
- Foomatic-RIP is installed and processes the printer.

## Procedure

1. Enumerate printers and available filters.
2. Create a printer with a malicious attribute.
3. Send a test page or job.
4. Verify execution as `lp` and look for the next hop.

## Commands

```bash
curl -s http://<HOST>:631/printers/
lpadmin -h <HOST>:631 -p evil -E -v ipp://<HOST>:631/printers/evil
lp -h <HOST>:631 -d evil /etc/hostname
# Malicious printer attribute
cupsFilter="application/pdf|/bin/sh -c id"
```

## Variants

- Modify an existing printer with `lpadmin -P`.
- Use the model name or PPD to inject.
- Combine it with a spool job for escalation.

## Limitations

- Administration may require authentication.
- The filter must be enabled for the MIME type.
- The process may run in a container without tools.

## Mitigation

- Restrict CUPS administration to localhost.
- Update Foomatic and validate attributes.
- Run CUPS unprivileged and clean the spool.

## Detection

- New printers or attribute changes.
- Jobs spawning processes from Foomatic-RIP.
- Remote access to port `631`.

## References

- [0xdf — EvilCUPS](https://0xdf.gitlab.io/2024/10/02/htb-evilcups.html)
- [CUPS — Documentation](https://openprinting.github.io/cups/doc/)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
