---
topic: WMI persistence
tags: [windows, wmi, persistence, event-consumer, sysmon, dfir]
---

# WMI persistence

**English** | [🇪🇸 Español](wmi-persistence.md)

## Concept

WMI can register a permanent subscription that runs an action when an event occurs. The typical chain combines `__EventFilter`, `CommandLineEventConsumer` and `FilterToConsumerBinding`; the consumer runs with WMI service privileges and survives reboots.

## When it applies

- Persistence without a conventional service or task.
- Recurring execution triggered by system events.
- Suspicion of a malicious WMI consumer.
- Sysmon or WMI repository analysis.

## Procedure

1. Enumerate filters, consumers and bindings.
2. Review names, queries and command lines.
3. Correlate with Sysmon 19, 20 and 21.
4. Compare with legitimate installed software.
5. Remove the subscription and preserve evidence.

```powershell
Get-WmiObject -Namespace root\Subscription -Class __EventFilter
Get-WmiObject -Namespace root\Subscription -Class CommandLineEventConsumer
Get-WmiObject -Namespace root\Subscription -Class __FilterToConsumerBinding
```

## Variants

- Command-line consumer.
- Script or ActiveScript consumer.
- Filter based on process, registry or time.
- Persistence in the WMI repository.

## Limitations

- The repository may require high privileges.
- Sysmon must have the events enabled.
- Legitimate tools also use WMI.
- Removing without preserving evidence destroys proof.

## Mitigation and detection

- Audit the `root\Subscription` namespace.
- Enable Sysmon 19–21 and centralise events.
- Restrict WMI subscription creation.
- Alert on consumers using PowerShell, `cmd` or user paths.

## References

- <https://learn.microsoft.com/en-us/windows/win32/wmisdk/receiving-a-wmi-event>
- <https://attack.mitre.org/techniques/T1546/003/>
- <https://www.sans.org/white-papers/wmi-forensics/>
