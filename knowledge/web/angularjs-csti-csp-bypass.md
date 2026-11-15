---
topic: AngularJS — CSTI y bypass de CSP
tags: [web, angularjs, csti, csp, xss]
---

# AngularJS — CSTI y bypass de CSP

[🌐 English](angularjs-csti-csp-bypass.en.md) | **Español**

## Concepto

AngularJS interpreta expresiones dentro del HTML. Si el usuario controla una plantilla, puede ejecutar expresiones y directivas `ng-*`; una CSP que permita `unsafe-eval` o scripts de AngularJS no impide el CSTI.

## Cuándo aplica

- La entrada se inserta en una zona con `ng-app`.
- No se usa `ng-non-bindable` ni escape.
- La CSP permite `unsafe-eval` o el bundle de Angular.

## Procedimiento

1. Confirmar la evaluación con `{{7*7}}`.
2. Usar `ng-init`/`ng-click` para ejecutar.
3. Exfiltrar cookies o encadenar OAuth/CSRF.
4. Automatizar el robo de sesión del bot.

## Comandos

```bash
{{7*7}}
<div ng-app ng-init="$eval('...')">x</div>
# o usar ng-click/ng-focus para el bot

```

## Variantes

- `ng-focus` con autofocus.
- `$sce.trustAsHtml` mal usado.
- CSP con nonce reutilizado.

## Limitaciones

- `ng-csp` y `ng-non-bindable` bloquean.
- Una CSP estricta sin `unsafe-eval` puede impedir.
- El bot puede no visitar el contenido.

## Mitigación

- Escapar HTML y usar `ng-non-bindable`.
- CSP sin `unsafe-eval` y con nonces.
- Sanitizar el HTML en servidor.

## Detección

- `{{...}}` o `ng-*` en contenido de usuario.
- CSP reports de `unsafe-eval`.
- Peticiones del bot a dominios externos.

## Referencias

- [0xdf — Eloquia](https://0xdf.gitlab.io/2026/10/17/htb-eloquia.html)
- [AngularJS — security guide](https://docs.angularjs.org/guide/security)
- [PortSwigger — CSTI](https://portswigger.net/kb/issues/00200901_client-side-template-injection)
