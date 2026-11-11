---
title: "Invisible characters and Unicode backdoors"
tags: [misc, unicode, javascript, backdoor, code-review]
---

# Invisible characters and Unicode backdoors

**English** | [🇪🇸 Español](unicode-invisible.md)

## 1. When to look here

Code that "looks normal" behaves differently: a variable that is not there, an odd trailing comma, a comparison that always fails. Invisible characters are cheap obfuscation and hard to spot in an editor.

## 2. The ones seen in challenges

| Character | Code point | Looks like | Typical use |
|---|---|---|---|
| HANGUL FILLER | `U+3164` | a space | valid JS identifier |
| ZERO WIDTH SPACE | `U+200B` | nothing | split tokens or mark |
| ZERO WIDTH JOINER | `U+200D` | nothing | join emoji; also obfuscates |
| WORD JOINER | `U+2060` | nothing | prevent breaks |
| RIGHT-TO-LEFT OVERRIDE | `U+202E` | reverses visual order | hide extensions |
| Cyrillic homoglyphs | `U+0430`… | same as `a`, `e`, `o` | impersonate identifiers |

In JavaScript, `U+3164` is in the *Letter, other* category and is a legal identifier. That is why `const { choice,ㅤ} = req.body;` declares a second variable nobody sees.

## 3. Detection

`cat -A` turns them into escaped bytes and does not reveal the code point; `xxd` does:

```bash
grep -nP "[^\x00-\x7F]" app.js
python3 -c "import unicodedata,sys;print([unicodedata.name(c) for c in open('app.js').read() if ord(c)>127])"
```

Editors: VS Code highlights invisible and confusable characters by default since 1.63 (U+3164 included); vim does not. A linter rule (`no-irregular-whitespace`, `non-ascii`) helps in CI.

## 4. Typical case

An endpoint that only accepts indexes into a fixed list yet runs a client-chosen command. The array has a trailing comma that looks stylistic and actually adds a variable read from the request body: index 6 passes the bounds check because `commands.length` already includes the injected element.

## 5. Bidi and extensions

`U+202E` reverses rendering: `report\u202Efdp.exe` displays as `reportexe.pdf`. In file names, combined with homoglyphs it can fool a user and sometimes an extension check. NFC/NFKC normalisation does not strip bidi: control categories must be rejected.

## 6. Mitigation

- Reject any character outside an allowed set during validation (printable ASCII for keys and identifiers).
- Strict body schemas: numeric `choice` and no extra keys.
- Never build command lists from request data.
- In code review, search for `U+3164`, `U+200B` and bidi; a diff that "changes nothing" may be adding a variable.

## 7. Production detection

- WAF/validation with a character allowlist on parameters and field names.
- Alerts on non-ASCII form keys or invisible spaces.
- In logs, compare the number of received keys with the expected ones.

References: Unicode TR39 (confusables), Certitude's article on the invisible backdoor and the ECMAScript identifier documentation.
