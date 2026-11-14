---
topic: Crontab UI
tags: [linux, crontab-ui, cron, privesc, web-ui, scheduling]
---

# Crontab UI

**English** | [🇪🇸 Español](crontab-ui.md)

## Concept

Crontab UI is a web interface for managing cron jobs. If it runs as root and allows jobs to be created or edited, a user with access can schedule a privileged command. The abuse needs no memory corruption: it is exposed functionality with excessive permissions.

## When it applies

- Crontab UI listening on localhost or the network.
- Unauthenticated access or weak credentials.
- The process running as root.
- A writable jobs directory.

## Procedure

1. Identify the service and its user.
2. Review authentication and existing jobs.
3. Create a job that runs a harmless command.
4. Confirm execution as root.
5. Use the job to read files or establish persistence.

```bash
ps aux | grep -i crontab
crontab -l
curl -s http://127.0.0.1:8000/
```

## Variants

- An unauthenticated panel.
- Default credentials.
- A job writing to `/etc/sudoers` or spawning a shell.
- Persistence through a recurring job.

## Limitations

- The panel must allow job creation or editing.
- The process must run with privileges.
- The job may take time to execute.
- Some panels restrict commands.

## Mitigation and detection

- Do not run cron panels as root.
- Require authentication and limit commands.
- Audit crontab and `/etc/cron.*` changes.
- Alert on new jobs with shells or sensitive writes.

## References

- <https://github.com/alseambusher/crontab-ui>
- <https://attack.mitre.org/techniques/T1053/003/>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
