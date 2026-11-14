---
topic: Moodle — RCE through a malicious plugin
tags: [web, moodle, plugin, rce, xss]
---

# Moodle — RCE through a malicious plugin

[🌐 Español](moodle-plugin-rce.md) | **English**

## Concept

Moodle lets an administrator install plugins from a ZIP. Once an administrator session is obtained —for example through stored XSS that steals the cookie— a `local` plugin containing PHP can be uploaded and executed from a reachable path.

## When it applies

- Legacy Moodle with self-enrolment or editable profiles.
- Third-party plugins without review and a reachable `dataroot`.
- Stored XSS in messages, badges or course names.

## Procedure

1. Fingerprint the version and theme via `/lib/upgrade.txt` or assets.
2. Obtain an administrator session through XSS or reused credentials.
3. Build a minimal `local` plugin with `version.php` and a PHP page.
4. Upload it from `Site administration > Plugins > Install plugins`.
5. Request the plugin page and obtain a shell.

## Commands

```bash
# Package a minimal local plugin
zip -r moodle-rce.zip moodle-rce
# Authenticated upload (admin session and sesskey required)
curl -s -b cookies.txt -F 'repo_upload_file=@moodle-rce.zip' \
  'http://<HOST>/admin/tool/installaddon/index.php?sesskey=<SESSKEY>'
```

## Variants

- Profile XSS to steal `MoodleSession`.
- Install a theme or filter instead of a `local` plugin.
- Abuse a vulnerable legitimate plugin to run PHP.

## Limitations

- An account allowed to install plugins is required.
- The ZIP must follow the `moodle-rce/version.php` layout.
- Installation may need confirmation and write permissions.

## Mitigation

- Keep Moodle and plugins patched.
- Limit plugin installation to trusted administrators.
- Apply CSP and output encoding to reduce session theft.

## Detection

- New or modified plugins outside a maintenance window.
- Requests to `admin/tool/installaddon` and writes under `dataroot`.

## References

- <https://moodle.org/security/>
- <https://community.owasp.org/attacks/xss/>
