---
topic: Unicode — normalisation and path traversal
tags: [web, unicode, normalization, path-traversal, lfi, nfkc]
---

# Unicode — normalisation and path traversal

[🌐 Español](unicode-normalization-path-traversal.md) | **English**

## Concept

A filter that looks for `../` before normalising can let through characters that become dots after Unicode normalisation. `U+2025` (two dot leader, `‥`) normalises to `..` under NFKC. If the filesystem or framework normalises after the filter, the traversal executes.

## When it applies

- The application filters `../` or `..\\` in input.
- The string is normalised (NFKC/NFKD) or processed by an API that does.
- The parameter builds a file path.
- The language or framework normalises when opening the resource.

## Procedure

1. Confirm the filter and which variants it blocks.
2. Try characters that normalise to `.` or `/`.
3. Build the sequence equivalent to `../`.
4. Read a known file to validate.
5. Escalate to configuration, keys or source code.

## Commands

```text
/display/?page=..%E2%80%A5/..%E2%80%A5/app.py
# U+2025 normalises to ".." under NFKC
```

```python
import unicodedata
print(unicodedata.normalize("NFKC", "\u2025"))  # ..
```

## Variants

- `U+FF0E` (fullwidth dot) and `U+FF0F` (fullwidth slash).
- Filesystem normalisation (macOS, Windows).
- Double normalisation: once in the filter and once on open.

## Limitations

- The framework must normalise after the filter.
- Some filesystems do not normalise.
- The path must be valid for the process.
- Later filters may block the result.

## Mitigation

- Normalise to NFKC before validating.
- Resolve with `realpath` and check the allowed prefix.
- Use allowlists of pages or identifiers.
- Never build paths from user input.

## Detection

- Parameters with unusual Unicode characters.
- Paths containing `U+2025`, `U+FF0E` or overlong encodings.
- `app.py`, `.env` or key reads from the web server.
- File-open errors with normalised paths.

## References

- [Unicode — UAX #15](https://unicode.org/reports/tr15/)
- [OWASP — Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [0xdf — Unicode](https://0xdf.gitlab.io/2022/05/07/htb-unicode.html)
