---
topic: XPath injection
tags: [web, xpath, xml, injection, auth-bypass]
---

# XPath injection

[🌐 Español](xpath-injection.md) | **English**

## Concept

An XPath query built by concatenating user input lets an attacker change node selection. Authentication can be bypassed, the XML document enumerated and values extracted node by node.

## When it applies

- A login or search backed by XML.
- Parameters reflected in XPath errors.
- Applications validating users against an XML file.

## Procedure

1. Try single and double quotes and observe errors.
2. Attempt a bypass with `' or '1'='1`.
3. Determine the number of nodes and the structure.
4. Extract strings with `substring` and boolean comparisons.
5. Reuse any recovered credentials.

## Commands

```text
' or '1'='1
' or name()='user' or '1'='2
' or substring(//user[1]/password,1,1)='a' or '1'='2
```

## Variants

- Blind injection through boolean responses.
- Errors leaking the path or node name.
- XPath over user-uploaded documents.

## Limitations

- The parser may escape quotes.
- The query may use precompiled variables.
- Errors may be suppressed.

## Mitigation

- Use parameterized XPath or variables.
- Validate and normalize input.
- Do not expose parser errors.

## Detection

- Quotes and boolean operators in parameters.
- XPath errors and anomalous queries.

## References

- <https://community.owasp.org/attacks/XPATH_Injection>
- <https://attack.mitre.org/techniques/T1190/>
