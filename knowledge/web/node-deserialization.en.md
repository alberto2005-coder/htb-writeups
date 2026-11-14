---
topic: Insecure deserialization in Node.js
tags: [web, nodejs, deserialization, node-serialize, rce, cookies]
---

# Insecure deserialization in Node.js

**English** | [🇪🇸 Español](node-deserialization.md)

## Concept

`node-serialize` serializes JavaScript objects, including functions, and rebuilds them with `unserialize`. If the data comes from a cookie or user-controlled parameter, a serialized function executes when deserialized.

## When it applies

- Cookies or parameters containing JSON that starts with `{"` and includes `_$$ND_FUNC$$_`.
- Node.js apps using `node-serialize`, misconfigured `serialize-javascript` or `eval`.
- Sessions storing full objects on the client.

## Procedure

1. Decode the cookie (base64 or URL encoding).
2. Identify the structure and the serialized key.
3. Check whether the value is passed to `unserialize`.
4. Build an object with an immediately invoked function.
5. Send the encoded cookie and observe execution.

```javascript
const payload = {
  rce: "_$$ND_FUNC$$_function(){return require('child_process').execSync('id').toString()}()"
};
Buffer.from(JSON.stringify(payload)).toString("base64");
```

## Variants

- `_$$ND_FUNC$$_` with an immediately invoked function `()`.
- `eval` on JSON instead of `JSON.parse`.
- Prior prototype pollution to alter the deserialized object.
- Gadget chains in libraries that accept objects.

## Limitations

- The app must call `unserialize` on user input.
- Functions do not survive plain `JSON.parse`.
- WAF and cookie validation may block the payload.
- The execution context limits available commands.

## Mitigation and detection

- Do not deserialize executable objects; use `JSON.parse` and schema validation.
- Sign and encrypt cookies; never trust their content.
- Avoid `eval` and `Function` on external data.
- Alert on `_$$ND_FUNC$$_`, `child_process` and abnormally long cookies.

## References

- <https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data>
- <https://cwe.mitre.org/data/definitions/502.html>
- <https://attack.mitre.org/techniques/T1059/007/>
- <https://github.com/luin/serialize>
