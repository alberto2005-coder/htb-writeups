---
topic: Azure DevOps pipeline abuse
tags: [cloud, azure-devops, cicd, pipeline, service-connection, privesc]
---

# Azure DevOps pipeline abuse

**English** | [🇪🇸 Español](azure-devops-pipeline-abuse.md)

## Concept

An Azure DevOps pipeline runs code defined in the repository with the agent's credentials and often with access to service connections. If an attacker can modify the YAML or a task, they can run commands on the agent, read secrets and deploy to production.

## When it applies

- Repositories whose pipelines the compromised user can edit.
- Self-hosted agents running as privileged accounts.
- Pipeline variables holding secrets.
- Service connections with broad permissions.

## Procedure

1. Enumerate repositories and `azure-pipelines.yml` files.
2. Review variables, tasks and agents.
3. Identify a branch or PR that triggers the pipeline.
4. Add a step that reads the environment or credentials.
5. Run it and review logs/artifacts.

```yaml
- script: |
    whoami
    env | sort
  displayName: diagnostics
```

## Variants

- YAML modification on a personal branch.
- Inline script in an existing task.
- Abusing a service connection to deploy.
- Self-hosted agent with host access.
- Poisoned artifact consumed by another pipeline.

## Limitations

- Permission to edit the pipeline or branch is required.
- Approvals and environments protect deployments.
- Secrets may be masked in logs.
- Ephemeral agents reduce persistence.

## Mitigation and detection

- Separate PR and production pipelines with approvals.
- Use ephemeral agents and least-privilege accounts.
- Restrict service connections and secret variables.
- Audit YAML changes, manual runs and out-of-hours deployments.

## References

- <https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview>
- <https://attack.mitre.org/techniques/T1195/>
- <https://attack.mitre.org/techniques/T1078/004/>
- <https://owasp.org/www-project-top-ten/2017/A8_2017-Insecure_Deserialization>
