---
topic: WebAssembly — buffer overflow and stored XSS
tags: [web, wasm, buffer-overflow, xss, rails, memory]
---

# WebAssembly — buffer overflow and stored XSS

[🌐 Español](wasm-buffer-overflow-xss.md) | **English**

## Concept

A WebAssembly module written in C copies strings into fixed-size buffers without checking length. Although WASM runs in a sandbox, the overflow corrupts the module's own linear memory: it can overwrite an adjacent field that is later inserted into the DOM. If the overwritten value contains HTML, it becomes stored XSS.

## When it applies

- The application uses WASM to render or process user data.
- The binary uses `strcpy`, `memcpy` or unbounded loops.
- The module output is inserted with `innerHTML` or unescaped templates.
- A user can register or post content that an administrator reviews.

## Procedure

1. Locate the `.wasm` module and its exported functions.
2. Identify buffers and offsets (`wasm2wat` or Ghidra).
3. Send a long string and observe which field changes.
4. Place the HTML at the exact offset and publish the content.
5. Wait for the bot or administrator to load the page.

## Commands

```bash
wasm2wat app.wasm -o app.wat
# look for memory.copy / memory.fill calls and fixed sizes
python3 -c 'print("A"*48 + "<img src=x onerror=alert(1)>")'
```

## Variants

- Overwrite a date, name or counter that is rendered afterwards.
- Use the overflow to change a control decision.
- Combine it with a `fetch` that loads an external script.
- XSS that exfiltrates the administration panel HTML.

## Limitations

- The offset depends on the build and allocator.
- WASM cannot escape the browser sandbox.
- The field must reach the DOM unescaped.
- The bot must visit the content.

## Mitigation

- Use length-bounded functions (`strlcpy`, `snprintf`).
- Validate and truncate on the server.
- Escape output and use `textContent`.
- Build with `-fsanitize=address` in development.

## Detection

- Abnormally long strings in logs and forms.
- HTML in fields that should be dates or numbers.
- Bot requests to external domains.
- Memory errors or module restarts.

## References

- [MDN — WebAssembly](https://developer.mozilla.org/en-US/docs/WebAssembly)
- [OWASP — XSS](https://owasp.org/www-community/attacks/xss/)
- [0xdf — Derailed](https://0xdf.gitlab.io/2023/07/22/htb-derailed.html)
