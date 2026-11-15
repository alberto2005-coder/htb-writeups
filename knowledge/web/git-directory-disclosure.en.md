---
topic: Git — exposed repository and source recovery
tags: [web, git, source-code, credentials, git-dumper]
---

# Git — exposed repository and source recovery

**English** | [🌐 Español](git-directory-disclosure.md)

## Concept

An accessible `.git` allows rebuilding the repository, reading history and recovering configuration that should never have been published. It is a source leak and often exposes database credentials or API keys.

## When it applies

- `/.git/HEAD` returns 200.
- The server does not block hidden files.
- The repository contains deployment configuration.

## Procedure

1. Confirm the repository with `curl` or `nmap http-git`.
2. Rebuild it with `git-dumper`.
3. Review `git log`, branches and `settings.php`/`.env`.
4. Use the credentials for the CMS or database.

## Commands

```bash
curl -s http://<HOST>/.git/HEAD
git-dumper http://<HOST>/.git repo
git -C repo log --all --oneline
grep -R "password\|mysql://\|SECRET" repo
```

## Variants

- Exposed `.svn` or `.hg`.
- `settings.php.bak` backups.
- Tokens in old commits.

## Limitations

- The server may 404 loose objects.
- The repository may be empty or lack configuration.
- Credentials may be rotated.

## Mitigation

- Block `.git` at the web server.
- Keep secrets out of the repository; use environment variables.
- Rotate credentials if exposed.

## Detection

- Requests to `/.git/` and Git objects.
- `pack` or `HEAD` downloads from the Internet.
- Repository credentials used from unusual IPs.

## References

- [git-dumper — GitHub](https://github.com/arthaud/git-dumper)
- [0xdf — Dog](https://0xdf.gitlab.io/2025/07/12/htb-dog.html)
- [Git — security](https://git-scm.com/book/en/v2/Git-on-the-Server-Security)
