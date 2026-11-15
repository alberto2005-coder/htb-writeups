---
topic: .NET Remoting and WCF — deserialization and endpoints
tags: [windows, dotnet, remoting, wcf, ysoserial]
---

# .NET Remoting and WCF — deserialization and endpoints

**English** | [🌐 Español](dotnet-remoting-wcf.md)

## Concept

.NET Remoting with `BinaryFormatter` deserializes channel objects and can run gadgets. WCF may expose endpoints with privileged operations that execute PowerShell or commands. The usual chain is deserialization for the first user and a poorly protected WCF endpoint for SYSTEM.

## When it applies

- A .NET Remoting service uses a binary formatter.
- WCF exposes an administrative or execution endpoint.
- The port is reachable from the internal network.

## Procedure

1. Enumerate .NET services and channels.
2. Generate the gadget with `ysoserial.net`.
3. Send it to the remote channel and obtain a shell.
4. Decompile the WCF service and find the privileged endpoint.

## Commands

```bash
nmap -Pn -sCV -p135,445,5985 <IP>
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -c "calc" -o raw > payload.bin
python3 remoting_client.py <IP> payload.bin
dnSpy.exe <SERVICE>.exe
# WCF endpoint
python3 wcf_client.py --host <HOST> --command whoami
```

## Variants

- Use `ObjectDataProvider` or `WindowsIdentity` as the gadget.
- Abuse a WCF `NetTcpBinding` endpoint without authentication.
- Chain it with service credential theft.

## Limitations

- The gadget must exist on the server.
- WCF may require authentication.
- The firewall may limit the channel.

## Mitigation

- Remove .NET Remoting and `BinaryFormatter`.
- Authenticate and authorize every WCF endpoint.
- Run services with low-privilege accounts.

## Detection

- Binary .NET Remoting traffic from unusual hosts.
- WCF service child processes.
- WCF endpoints published without authentication.

## References

- [ysoserial.net](https://github.com/pwntester/ysoserial.net)
- [0xdf — Sharp](https://0xdf.gitlab.io/2021/05/01/htb-sharp.html)
- [Microsoft — WCF security](https://learn.microsoft.com/en-us/dotnet/framework/wcf/security-in-wcf)
