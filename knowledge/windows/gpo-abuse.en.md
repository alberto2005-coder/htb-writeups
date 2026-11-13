---
topic: GPO abuse
tags: [windows, active-directory, gpo, sharpgpoabuse, system, persistence]
---

# GPO abuse

**English** | [🇪🇸 Español](gpo-abuse.md)

## Concept

A user with rights to create or modify Group Policy Objects can add tasks, scripts or settings that apply to computers or OUs. If the GPO reaches a domain controller or privileged server, the task runs as SYSTEM and enables lateral movement or persistence.

## When it applies

- Membership in `Group Policy Creator Owners`.
- `WriteProperty` or `WriteDacl` rights over a GPO.
- A target OU containing privileged computers.
- Ability to force `gpupdate` or wait for application.

## Procedure

1. Enumerate GPOs and permissions with BloodHound.
2. Identify a modifiable OU or GPO.
3. Create a GPO or edit an existing one.
4. Add an immediate task or script.
5. Apply the policy and receive execution as SYSTEM.

```powershell
New-GPO -Name "upd-$(Get-Date -UFormat %s)"
.\SharpGPOAbuse.exe --addcomputertask --gponame <GPO> \
  --command powershell.exe --arguments "-EncodedCommand <B64>"
gpupdate /force
```

## Variants

- Immediate task at startup.
- Startup or shutdown script.
- Service or registry configuration.
- Editing an existing GPO with delegated rights.

## Limitations

- Permissions over the GPO or OU are required.
- The policy must reach the target computer.
- Application may require a reboot or `gpupdate`.
- Change control and EDR may detect the task.

## Mitigation and detection

- Audit `Group Policy Creator Owners` and GPO ACLs.
- Restrict GPO editing to domain administrators.
- Monitor events 5136, 4662 and immediate task creation.
- Review `gpupdate` and child processes spawned by GPO.

## References

- <https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn581922(v=ws.11)>
- <https://github.com/Flangvik/SharpGPOAbuse>
- <https://attack.mitre.org/techniques/T1484/001/>
