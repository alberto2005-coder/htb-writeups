---
sherlock: Ultimatum
domain: DFIR / Web
difficulty: Easy
platform: Hack The Box
evidence: Logs and files from a compromised WordPress site
tools: [grep, access.log, WP-CLI, diff]
---

# Ultimatum — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A **WordPress** blog starts misbehaving and the team suspects a plugin. You are given the site's logs and file tree to identify the vector, its scope and how to restore it.

## Evidence

- Web server logs (access/error) plus a copy of the WordPress tree.

## Method

1. **When it started**: sort `access.log` by hour and look for bursts against one plugin.

```bash
awk '{print $4, $7}' access.log | sort | uniq -c | sort -rn | head
grep -i 'wp-content/plugins' access.log | awk '{print $7}' | sort | uniq -c | sort -rn
```

2. **Vector**: an outdated plugin with a vulnerable route (`admin-ajax.php?action=...`, upload or LFI). Compare against the published version.

```bash
grep -r "Version:" wp-content/plugins/<plugin>/ | sort -u
```

3. **Execution**: POSTs to the vulnerable endpoint and odd 200 responses; new files appear in `wp-content/uploads` right after.

4. **Persistence**: a new admin user in the database, `mu-plugins`, modified themes, WP cron jobs.

```bash
wp user list --role=administrator
```

5. **Restore**: reinstall the plugin and core from official packages, rotate credentials, and diff `wp-config.php`.

## What it teaches

- `access.log` gives the order of events: scan, exploit, upload.
- An unpatched plugin is the most common WordPress vector.
- Restoring is not just copying files back: rotate credentials and check persistence.

## Pitfalls

- **Mixed traffic**: separate legitimate requests (bots, feeds) by *user-agent* and time.
- **Obfuscated files**: a modified `functions.php` hides well; diff against the original.
- **Caching**: behind a CDN, part of the attack never reaches the origin log.
