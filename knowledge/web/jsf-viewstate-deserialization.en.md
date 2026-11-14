---
topic: JSF ViewState — Java deserialization
tags: [web, java, jsf, viewstate, deserialization]
---

# JSF ViewState — Java deserialization

[🌐 Español](jsf-viewstate-deserialization.md) | **English**

## Concept

JavaServer Faces sends view state in `javax.faces.ViewState`. If the server deserializes it without encryption or signing, a malicious serialized object can execute code through a gadget chain.

## When it applies

- JSF/MyFaces or Mojarra applications with Base64 ViewState.
- Large `javax.faces.ViewState` values or ones beginning with `rO0AB`.
- Servers with vulnerable Java libraries on the classpath.

## Procedure

1. Capture the `ViewState` parameter from a POST.
2. Decode it and check for the `rO0AB` Java serialization magic.
3. Identify the JSF library and version.
4. Generate a compatible gadget chain.
5. Replace the ViewState and send the request.

## Commands

```bash
echo '<VIEWSTATE>' | base64 -d | xxd | head
java -jar ysoserial.jar CommonsCollections5 'id' | base64 -w0
```

## Variants

- ViewState encrypted with a known or default key.
- Mojarra with compressed or encrypted ViewState.
- Deserialization in cookies or session parameters.

## Limitations

- ViewState may be signed or encrypted.
- The gadget chain must exist on the classpath.
- WAFs may block large Base64 payloads.

## Mitigation

- Configure signed and encrypted ViewState.
- Patch JSF and Java libraries.
- Avoid deserializing user-controlled data.

## Detection

- ViewState containing unexpected `rO0AB` magic or anomalous sizes.
- Deserialization errors and Java processes spawning commands.

## References

- <https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data>
- <https://attack.mitre.org/techniques/T1190/>
