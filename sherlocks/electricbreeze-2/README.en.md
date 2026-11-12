---
sherlock: ElectricBreeze-2
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, java, jar, webshell, credential-theft, volt-typhoon]
---

# ElectricBreeze-2 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original sample or real IOCs.

## TL;DR

JAR sample associated with a Volt Typhoon-style actor. The bytecode is decompiled to identify the webshell, obfuscation, encrypted communication and credential access.

## Scenario

A Java server shows an uninventoried JAR and outbound connections. The sample and logs are provided to determine its function and persistence.

## Artefacts

- JAR and compiled classes.
- Embedded configuration/resources.
- Process and network logs.
- Webroot and created files.

## Methodology

1. Hash the JAR and list its contents.
2. Decompile with `jadx`/`CFR` and review bootstrap classes.
3. Locate webshell strings, commands and URLs.
4. Identify C2 encryption/configuration.
5. Correlate with the Java process and webroot.

```bash
unzip -l sample.jar
jadx sample.jar -d out
grep -R "Runtime.getRuntime" out
```

## Sample questions

- Which class implements the webshell?
- Which parameters does it accept and execute?
- How does it encrypt communication?
- Which credentials or files does it read?
- How does it start and persist?

## Tools

`jadx`, `CFR`, `unzip`, `strings`, `Wireshark`.

## Evidence and redaction

Hashes, classes and screenshots are kept with URLs, users and paths redacted.

## Lessons learned

- Java is easy to decompile and read.
- JSP/Java webshells often use `Runtime.exec`.
- Embedded configuration reveals C2 and keys.
- A misplaced JAR may run during deployment.

## Detection

- Inventory JARs and hashes on servers.
- Alert on `Runtime.exec` from web applications.
- Review outbound Java connections.
- Apply YARA to JAR/class files.

## References

- <https://app.hackthebox.com/sherlocks/ElectricBreeze-2>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://github.com/skylot/jadx>
