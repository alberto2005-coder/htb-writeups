---
sherlock: Psittaciformes
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, bash-history, git, log-analysis, web]
---

# Psittaciformes — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A Linux server shows suspicious activity and a Git repository contains unexplained changes. The analyst must reconstruct access, executed commands and attacker-introduced code.

## Evidence

- `auth.log`, `syslog` and web-service logs.
- `.bash_history` for relevant accounts.
- Git repository with history and branches.
- Configuration files and cron jobs.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigation

### 1. Access and session

Accepted logins, repeated failures and user creation are located. The source IP is correlated with SSH logs and the first command in shell history.

```bash
grep -Ei 'accepted|failed|new user|sudo' auth.log
```

### 2. Command history

`.bash_history` has no timestamps by default; it is ordered against authentication events and the `atime`/`mtime` of touched files. Downloads, permission changes and script execution are identified.

- Reconnaissance commands.
- Tool transfer.
- Code or configuration edits.
- Persistence through cron or a service.

### 3. Git repository

`git log`, `git diff` and loose objects are reviewed. Attacker commits may be hidden in branches, the reflog or unreferenced blobs.

```bash
git log --all --oneline --decorate
git reflog
git fsck --lost-found
```

Modified code is compared with the deployed version to determine whether it reached production.

## Conclusions

- Access account and IP.
- Commands and modified files.
- Commit or blob containing the malicious change.
- IOCs: paths, names and hashes, redacted.

## Lessons

- Shell history without timestamps needs external correlation.
- Git retains objects even when a commit is no longer on a branch.
- A repository change does not mean it was deployed.

## References

- <https://www.hackthebox.com/sherlocks/Psittaciformes>
- <https://attack.mitre.org/techniques/T1070/003/>
- <https://git-scm.com/docs/git-fsck>
- <https://www.git-scm.com/book/en/v2/Git-Internals-Git-Objects>
