---
topic: Laravel — environment injection (CVE-2024-52301)
tags: [web, laravel, php, cve-2024-52301, auth-bypass]
---

# Laravel — environment injection (CVE-2024-52301)

**English** | [🌐 Español](laravel-env-injection.md)

## Concept

When `register_argc_argv` is enabled, Laravel may interpret query-string parameters as console arguments. An attacker changes `APP_ENV` with a parameter such as `--env=preprod`; if that environment skips authentication or enables debug, an internal route becomes public.

## When it applies

- The application is Laravel and PHP has `register_argc_argv=On`.
- Alternative environments (`local`, `staging`, `preprod`) have different controls.
- The site exposes debug output or a panel with an environment-based login bypass.

## Procedure

1. Fingerprint Laravel and check `APP_DEBUG` in error responses.
2. Try `?--env=local`, `?--env=staging` and `--env=preprod` variants.
3. Compare behaviour: skipped login, new routes or exposed debug.
4. Chain the access with the next vulnerability in the panel.

## Commands

```bash
curl -s "http://<HOST>/?--env=preprod" | head
curl -s "http://<HOST>/?--env=local" | grep -i "whoops\|debug\|login"
curl -s -o /dev/null -w "%{http_code}\n" "http://<HOST>/dashboard?--env=preprod"
```

## Variants

- Add the parameter to a specific route instead of the root.
- Combine `--env` with `--debug` when the framework accepts it.
- Use the environment change to alter the database or session storage.

## Limitations

- Requires `register_argc_argv=On`; many deployments disable it.
- It is not RCE by itself: it changes application configuration.
- The environment must exist and have a valid `.env.<environment>` file.

## Mitigation

- Disable `register_argc_argv` and update Laravel.
- Do not keep development environments reachable from production.
- Pin `APP_ENV` on the server and review per-environment configuration.

## Detection

- Requests with `--env=`, `--debug` or CLI arguments in the query string.
- Login behaviour changes tied to a parameter.
- Laravel errors exposing stack traces or environment variables.

## References

- [0xdf — Environment](https://0xdf.gitlab.io/2025/09/06/htb-environment.html)
- [NVD — CVE-2024-52301](https://nvd.nist.gov/vuln/detail/CVE-2024-52301)
- [Laravel — Configuration](https://laravel.com/docs/11.x/configuration)
