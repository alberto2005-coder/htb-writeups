---
topic: React2Shell — RSC deserialization (CVE-2025-55182)
tags: [web, react, nextjs, rsc, cve-2025-55182, deserialization, rce]
---

# React2Shell — RSC deserialization (CVE-2025-55182)

**English** | [🌐 Español](react2shell-rsc-rce.md)

## Concept

React Server Components deserializes client data for Server Actions. In vulnerable versions, a multipart payload manipulates the prototype chain and reaches `child_process`, allowing unauthenticated remote code execution.

## When it applies

- The app uses NextJS/React with RSC and Server Actions.
- The version is affected by CVE-2025-55182.
- A multipart POST with `Next-Action` can be sent.

## Procedure

1. Extract versions from JS chunks and headers.
2. Identify a valid Server Action.
3. Build the multipart body with the prototype chain.
4. Send with `curl` and verify execution.

## Commands

```bash
curl -s http://<IP>:3000 | grep -oE '/_next/static/[^"\\]+\.js'
curl -X POST http://<IP>:3000/ -H 'Next-Action: <ACTION>' \
  -H 'Content-Type: multipart/form-data; boundary=----R2S' \
  --data-binary @r2s-body.txt
```

## Variants

- Server Actions with different IDs.
- Prop deserialization in flight data.
- Chain with the Node inspector.

## Limitations

- Patched versions reject the payload.
- The app may not use Server Actions.
- A WAF may block multipart.

## Mitigation

- Update React/NextJS to fixed versions.
- Validate Server Action input.
- Never trust client data for deserialization.

## Detection

- POST with `Next-Action` and anomalous multipart bodies.
- Node child processes from the web server.
- Vulnerable versions in production.

## References

- [0xdf — Reactor](https://0xdf.gitlab.io/2026/10/03/htb-reactor.html)
- [NVD — CVE-2025-55182](https://nvd.nist.gov/vuln/detail/CVE-2025-55182)
- [React — security advisory](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)
