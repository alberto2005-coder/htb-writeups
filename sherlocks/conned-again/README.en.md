---
sherlock: Conned-Again
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, confluence, cve-2023-22515, cve-2023-22527]
---

# Conned-Again — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation note; no literal platform answers.
> Evidence described from the public scenario and technical writeups; no environment data is published.

## Scenario

Forela's Confluence server has been compromised. A **CatScale** triage of the Linux host is provided, and the investigation must reconstruct how the attacker obtained administrative access, what they changed and whether they deployed persistence. The case revolves around two Confluence CVEs: **CVE-2023-22515** (unauthorised administrator creation) and **CVE-2023-22527** (OGNL injection in templates).

## Evidence

- CatScale triage archive with the installation's filesystem.
- Confluence, Tomcat and front-proxy logs.
- Instance configuration (`confluence.cfg.xml`, `server.xml`, `web.xml`).
- Process, user and file metadata created during the incident window.

```bash
sha256sum conned-again.zip
unzip -l conned-again.zip | head -40
```

Record hashes before opening anything and work on a copy. Artefacts may contain credentials; redact them in notes.

## Investigation

### 1. Inventory and triage

Find the exact Confluence version and compare it with affected releases:

```bash
grep -R "confluence.version\|BuildNumber" opt/atlassian/confluence/ 2>/dev/null | head
grep -R "CVE-2023-2251\|CVE-2023-22527" . 2>/dev/null | head
```

Also check which user runs the service and from which directory it is served. Confluence exposed directly to the Internet without an authenticating proxy is the risk scenario.

### 2. Timeline

The main sources are access logs and Confluence logs. Look for:

```bash
grep -E "setupadministrator|setup/setup|text-inline|template/aui" logs/*.log | head -50
```

- Requests to `/setup/setupadministrator.action` outside the initial installation.
- Requests to `/template/aui/text-inline.vm` with OGNL parameters.
- Creation of administrator users and changes in `cwd_user`.
- Service restarts and JSP file deployment.

Normalise time zones: Confluence logs usually use the server zone, while the proxy may log UTC. Explain the offset before ordering events.

### 3. Key artifact

The sequence that cracks the case is two requests: one creates or elevates an administrative account, and another executes OGNL in the template. Look for the effect on disk:

```bash
grep -R "Runtime\|getRuntime\|ProcessBuilder" opt/atlassian/confluence/ 2>/dev/null | head
find . -name '*.jsp' -newermt '<START>' ! -newermt '<END>' 2>/dev/null
```

A new JSP in the working directory, an unrecognised administrator or a scheduled task created right after the request confirms execution. The absence of a JSP does not rule out the attack: OGNL can execute commands in memory.

## Findings

- The attacker exploited a vulnerable Confluence instance and created administrative access.
- Command execution happened in the context of the service user, not as root.
- Main IOCs are the two CVE paths, the source IP/User-Agent and users created outside corporate onboarding.
- Any credential visible in the configuration must be rotated.

## Lessons

- An exposed Confluence needs a proxy, authentication and rules that block `/setup/*` after installation.
- Patching is not enough if attacker-created administrators remain: review `cwd_user` and permissions.
- Application and proxy logs must be correlated by time and request identifier.
- A CatScale triage preserves the context needed to answer “what changed”, not just “what version was installed”.
