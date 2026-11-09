---
title: JenkreadD
category: DFIR / Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, jenkins, cve-2024-23897, file-read, logs]
---

# JenkreadD — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

## Scenario

An internet-facing **Jenkins** server has been probed. Evidence includes service logs, access history and host artifacts. Determine whether the CLI arbitrary file read (**CVE-2024-23897**) was exploited and what the attacker took.

## Evidence and triage

```bash
ls -la; grep -a "jenkins" *.log | head
EvtxECmd.exe -d . --csv out --csvf evtx.csv     # if EVTX is present
```

Useful artifacts: `jenkins.log`, `access_log`, `audit.log`, `$JENKINS_HOME/logs`, scheduled tasks and the service shell history.

## Method

- **CVE-2024-23897**: the CLI (`jenkins-cli.jar`) treats arguments starting with `@` as file paths; an error returns lines from the file. Logs show requests to `/cli` with `@/etc/passwd`, `@/var/jenkins_home/secrets/...` and similar.
- Look in `access_log` for **POST /cli** with `-webSocket` or `args4j` and 200/500 responses followed by large downloads.
- Review the Jenkins audit log: user creation, credential changes and job runs.
- With EVTX/Sysmon, cross-check **4688** for `java -jar jenkins-cli.jar` and **Sysmon 11** for new files.
- Confirm which files were read: `secrets/` keys, `credentials.xml` and `config.xml` lead to RCE.

## Findings (pattern)

```text
POST /cli  args="@<path>"  status=500
jenkins.log: "No such file" + first line of the file
audit.log: new user / job created
```

`@path` plus an error containing content is the CVE signature; a new job or user confirms impact.

## Lessons

- Arbitrary file read in Jenkins usually ends in RCE: `secrets/` and credentials live there.
- CLI logs are the main evidence; the error that leaks the file is recorded.
- Compare request volume with the baseline to separate scanning from exploitation.

## Detection and mitigation

- Update Jenkins (CVE-2024-23897) and disable the remote CLI when unused.
- Require authentication, use a minimal `authorizationStrategy` and segment the panel.
- Alert on `POST /cli` with `@` and repeated 500s.
- Rotate credentials and `secrets/` keys after exposure.

MITRE: T1190, T1005, T1059.
