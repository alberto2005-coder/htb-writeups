---
topic: Git — privilege escalation with hooks in writable repositories
tags: [linux, git, hooks, post-commit, systemd, privesc, encoding]
---

# Git — privilege escalation with hooks in writable repositories

**English** | [🌐 Español](git-hooks-privesc.md)

## Idea

Git runs scripts from `.git/hooks` at specific moments, such as `post-commit` after a commit. If an unprivileged user can write to `.git` and a privileged user commits to that repository, the hook runs with the second user's permissions. On Encoding, `www-data` could run `git-commit.sh` as `svc` and write to `.git`; a `post-commit` hook added an SSH key for `svc`.

## When it applies

- A privileged script runs `git add`/`git commit` on a repository.
- The web user can write to `.git` or its hooks.
- The script is launched through `sudo` or by a service running as another user.
- No protections such as a safe `core.hooksPath` or disabled hooks are in place.

## Procedure

1. Identify the script and the user it runs as.
2. Check permissions and ACLs on `.git` and `.git/hooks`.
3. Create a `post-commit` hook with the desired action.
4. Make the hook executable.
5. Trigger a change and run the privileged script.
6. Use the resulting key, file or shell.

## Commands

```bash
ls -ld .git .git/hooks
getfacl .git
printf '#!/bin/bash\nmkdir -p /home/<USER>/.ssh\necho "<PUBLIC_KEY>" >> /home/<USER>/.ssh/authorized_keys\n' > .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

```bash
# Trigger the commit from the privileged script
sudo -u <USER> /path/git-commit.sh
```

## Variants

- `pre-commit` hook to run before validation.
- `post-checkout` or `post-merge` when the flow does not commit.
- `core.hooksPath` pointing to a controlled directory.
- `.git/config` with `core.fsmonitor` or malicious aliases.
- Bare repositories and server-side hooks.

## Limitations

- The hook must be executable and the privileged user must run Git.
- `git commit --no-verify` skips `pre-commit`, not `post-commit`.
- Some configurations ignore hooks by default.
- The repository owner may prevent writes.
- The hook action is recorded in history and logs.

## Mitigation

- Do not allow unprivileged users to write to `.git`.
- Run commit scripts as the same user that writes the repository.
- Set `core.hooksPath` to a trusted, versioned directory.
- Review repository permissions and ACLs.
- Avoid `sudo` on scripts operating on shared repositories.

## Detection

- New or modified hooks under `.git/hooks`.
- Automated commits with unexpected authors.
- SSH keys added after a commit.
- Scripts under `.git/hooks` run by users other than the owner.
- Changes to `core.hooksPath` or repository configuration.

## References

- [0xdf — Encoding](https://0xdf.gitlab.io/2023/04/15/htb-encoding.html)
- [Git — Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Encoding writeup](../../machines/linux/encoding/README.en.md)
