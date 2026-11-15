---
title: WCF — command injection in a SOAP endpoint
tags: [windows, wcf, soap, dotnet, command-injection, privesc]
---

# WCF — command injection in a SOAP endpoint

[🇪🇸 Español](wcf-soap-command-injection.md) | **English**

## Concept

Windows Communication Foundation (WCF) exposes operations over SOAP. If a method takes a string and concatenates it into `Process.Start`, `cmd.exe` or PowerShell, the endpoint becomes remote execution. Many internal services only listen on `localhost`, so first get a shell on the host.

## When it applies

- A WCF service runs on an unusual port (for example, 8000).
- The contract can be read (`?wsdl`, `mex`) or the .NET client decompiled.
- The method accepts process names, paths or arguments.

## Procedure

1. Locate the endpoint and download the WSDL.
2. Enumerate operations and types with `svcutil` or `dotPeek`.
3. Build a SOAP envelope with the correct `SOAPAction`.
4. Inject a separator (`;`, `&`, `|`) and run a command.

```bash
curl -s 'http://localhost:8000/MonitorService?wsdl' -o service.wsdl
svcutil service.wsdl
```

```text
POST /MonitorService/ HTTP/1.1
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://tempuri.org/IMonitoringService/KillProcess"

<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <KillProcess xmlns="http://tempuri.org/">
      <processName>x; powershell -e <BASE64>; #</processName>
    </KillProcess>
  </soap:Body>
</soap:Envelope>
```

## Variants

- Inject into an argument passed to `cmd.exe /c`.
- Use `ProcessStartInfo.FileName` with a UNC path to load a binary.
- If the service runs as SYSTEM, execution is SYSTEM too.

## Limitations

- The endpoint may require Windows authentication or a specific binding.
- Some methods validate the name against a process allowlist.
- The WSDL may not be published; decompile the client instead.

## Mitigation and detection

- Never concatenate input into commands; use `ProcessStartInfo.ArgumentList`.
- Validate against an allowlist of processes.
- Run the service under a least-privilege account.
- Audit child processes of `w3wp.exe` or the WCF service.

## References

- <https://learn.microsoft.com/en-us/dotnet/framework/wcf/whats-wcf>
- <https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/security-overview>
- <https://owasp.org/www-community/attacks/Command_Injection>
