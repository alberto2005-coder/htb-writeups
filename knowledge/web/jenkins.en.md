---
topic: Jenkins
tags: [web, jenkins, groovy, ci-cd, credentials, rce]
---

# Jenkins

**English** | [🇪🇸 Español](jenkins.md)

## Concept

Jenkins exposes jobs, credentials and a Groovy console that can execute code on the server. An unauthenticated instance, weak credentials or script permissions can compromise CI/CD and the secrets it manages.

## When it applies

- `/manage` or `/script` reachable.
- Default or guest credentials.
- Parameterised jobs and scripts.
- Agents with access to repositories or production.

## Procedure

1. Enumerate version, plugins and jobs.
2. Test default credentials.
3. Review the script console.
4. Run a harmless command to confirm.
5. Extract credentials and pivot into CI/CD.

```bash
curl -s http://<HOST>:8080/api/json?tree=jobs[name,url]
curl -s --user "$JENKINS_AUTH" http://<HOST>:8080/script
```

## Variants

- An unauthenticated Groovy console.
- `jenkins-cli` with a user key.
- Credentials in jobs or variables.
- A compromised agent with internal network access.

## Limitations

- The console may require administrator.
- CSRF can block requests.
- Agents may be isolated.
- Secrets may be masked.

## Mitigation and detection

- Update Jenkins and plugins.
- Disable the console for non-admin users.
- Apply MFA and least privilege.
- Audit scripts, jobs and credential access.

## References

- <https://www.jenkins.io/doc/book/security/>
- <https://attack.mitre.org/techniques/T1195/>
- <https://owasp.org/www-project-top-ten/>
