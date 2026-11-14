---
topic: Gitea
tags: [web, gitea, git, repositories, credentials, source-code]
---

# Gitea

**English** | [🇪🇸 Español](gitea.md)

## Concept

Gitea is a self-hosted Git service that may expose repositories, users, tokens and configuration. An accessible repository may contain credentials, keys, pipelines or vulnerable code; an account with permissions can modify hooks or create a runner.

## When it applies

- An exposed Gitea instance.
- Public or guest repositories.
- Open registration.
- Tokens or keys in history.

## Procedure

1. Enumerate users, organisations and repositories.
2. Clone accessible repositories and review history.
3. Search code, issues and releases for secrets.
4. Review hooks, runners and deploy keys.
5. Reuse credentials against other services.

```bash
git clone http://<HOST>/<ORG>/<REPO>.git
git log --all --oneline
trufflehog git http://<HOST>/<ORG>/<REPO>.git
```

## Variants

- A private repository with guest access.
- An API token in a `.env` file.
- A hook that runs a command on the server.
- A runner with host access.

## Limitations

- Registration may be closed.
- Repositories may be empty or decoys.
- Secrets may be in deleted branches.
- Hooks require administrator rights.

## Mitigation and detection

- Restrict registration and visibility.
- Scan secrets and rotate credentials.
- Audit hooks, runners and deploy keys.
- Alert on bulk clones and integration changes.

## References

- <https://docs.gitea.com/>
- <https://attack.mitre.org/techniques/T1213/003/>
- <https://github.com/trufflesecurity/trufflehog>
