---
topic: AngularJS — CSTI and CSP bypass
tags: [web, angularjs, csti, csp, xss]
---

# AngularJS — CSTI and CSP bypass

**English** | [🌐 Español](angularjs-csti-csp-bypass.md)

## Concept

AngularJS evaluates expressions inside HTML. If the user controls a template, expressions and `ng-*` directives execute; a CSP allowing `unsafe-eval` or AngularJS scripts does not stop CSTI.

## When it applies

- Input is inserted into an `ng-app` area.
- `ng-non-bindable` or escaping is missing.
- CSP allows `unsafe-eval` or the Angular bundle.

## Procedure

1. Confirm evaluation with `{{7*7}}`.
2. Use `ng-init`/`ng-click` to execute.
3. Exfiltrate cookies or chain OAuth/CSRF.
4. Automate bot session theft.

## Commands

```bash
{{7*7}}
<div ng-app ng-init="$eval('...')">x</div>
# or use ng-click/ng-focus for the bot

```

## Variants

- `ng-focus` with autofocus.
- Misused `$sce.trustAsHtml`.
- CSP with a reused nonce.

## Limitations

- `ng-csp` and `ng-non-bindable` block it.
- A strict CSP without `unsafe-eval` may prevent it.
- The bot may not visit the content.

## Mitigation

- Escape HTML and use `ng-non-bindable`.
- CSP without `unsafe-eval` and with nonces.
- Sanitize HTML server-side.

## Detection

- `{{...}}` or `ng-*` in user content.
- CSP reports for `unsafe-eval`.
- Bot requests to external domains.

## References

- [0xdf — Eloquia](https://0xdf.gitlab.io/2026/10/17/htb-eloquia.html)
- [AngularJS — security guide](https://docs.angularjs.org/guide/security)
- [PortSwigger — CSTI](https://portswigger.net/kb/issues/00200901_client-side-template-injection)
