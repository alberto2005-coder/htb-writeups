---
topic: UnrealIRCd 3.2.8.1 backdoor
tags: [linux, unrealircd, backdoor, irc, cve-2010-2075, supply-chain]
---

# UnrealIRCd 3.2.8.1 backdoor

**English** | [🇪🇸 Español](unrealircd-backdoor.md)

## Concept

Version 3.2.8.1 distributed from the official site between 2009 and 2010 contained a backdoor. The binary accepted the `AB;` command followed by an instruction and ran it with the service's privileges.

## When it applies

- IRC service on port 6667.
- `UnrealIRCd` banner reporting version 3.2.8.1.
- Old containers or images without updates.
- Labs and challenges replicating the vulnerable version.

## Procedure

1. Identify the service and version with `nmap` or the banner.
2. Confirm the vulnerable version.
3. Send `AB;` with a test command.
4. Use a reverse shell if the command executes.
5. Check the service account.

```bash
nmap -Pn -sV -p 6667 <IP>
printf 'AB;id\n' | nc <IP> 6667
```

## Variants

- Direct command execution with `AB;`.
- Download and execution of a remote script.
- Service running as root in old images.
- Backdoor inserted into a supply-chain tarball.

## Limitations

- Only the compromised 3.2.8.1 distribution is affected.
- The service must accept the attacker's connection.
- Some deployments run the daemon as an unprivileged user.
- The version may be patched even if the banner imitates it.

## Mitigation and detection

- Update UnrealIRCd and verify package hashes.
- Run the service as a dedicated user without a shell.
- Restrict the port to trusted networks.
- Alert on `AB;` commands and child processes of the IRC daemon.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2010-2075>
- <https://www.exploit-db.com/exploits/16922>
- <https://attack.mitre.org/techniques/T1195/001/>
- <https://www.unrealircd.org/>
