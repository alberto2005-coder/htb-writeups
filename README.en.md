# 🎯 HTB Writeups — alberto2005coder

[🇪🇸 Español](README.md) | **English**

Personal repository of **Hack The Box** writeups, notes and methodology.

> **Status:** work in progress. **Active** machines are not published until HTB retires them.
>
> **Numbers:** 116 machines, 60 Sherlocks, 81 challenges and 66 knowledge topics (257 writeups), each in ES/EN.

---

## 👤 Profile

- **HTB:** [alberto2005coder](https://app.hackthebox.com/users/4187928)
- **Focus:** web pentesting, Linux, Active Directory and cloud.
- **Goal:** document the full process (recon → foothold → privilege escalation → mitigation), not just the final command.

---

## 🗂️ Machines

| Machine | OS | Difficulty | Category | State | Key techniques | ES | EN |
|---|---|---|---|---|---|---|---|
| Sizzle | Windows | Insane | Active Directory / ADCS | **Retired** | SCF/Responder, ADCS, Kerberoasting and DCSync | [ES](machines/windows/sizzle/README.md) | [Ver](machines/windows/sizzle/README.en.md) |
| Reel | Windows | Hard | Active Directory | **Retired** | RTF CVE-2017-0199, WriteOwner/WriteDacl ACLs and backup script | [ES](machines/windows/reel/README.md) | [Ver](machines/windows/reel/README.en.md) |
| Absolute | Windows | Insane | Active Directory / ADCS | **Retired** | AS-REP, shadow credentials, KrbRelay and DCSync | [ES](machines/windows/absolute/README.md) | [Ver](machines/windows/absolute/README.en.md) |
| Multimaster | Windows | Insane | Active Directory / MSSQL | **Retired** | SQLi, CEF debug, GenericWrite/AS-REP and Server Operators | [ES](machines/windows/multimaster/README.md) | [Ver](machines/windows/multimaster/README.en.md) |
| Authority | Windows | Medium | Active Directory / ADCS | **Retired** | Anonymous SMB, Ansible Vault, PWM, ESC1 on `CorpVPN` and PassTheCert | [ES](machines/windows/authority/README.md) | [Ver](machines/windows/authority/README.en.md) |
| Meow | Linux | Very Easy | Starting Point | Available | Unauthenticated FTP/Telnet | [ES](machines/starting-point/meow/README.md) | [Ver](machines/starting-point/meow/README.en.md) |
| Fawn | Linux | Very Easy | Starting Point | Available | Anonymous FTP | [ES](machines/starting-point/fawn/README.md) | [Ver](machines/starting-point/fawn/README.en.md) |
| Dancing | Windows | Very Easy | Starting Point | Available | SMB null session | [ES](machines/starting-point/dancing/README.md) | [Ver](machines/starting-point/dancing/README.en.md) |
| Redeemer | Linux | Very Easy | Starting Point | Available | Unauthenticated Redis | [ES](machines/starting-point/redeemer/README.md) | [Ver](machines/starting-point/redeemer/README.en.md) |
| Nibbles | Linux | Easy | CMS / Web | Retired (ref.) | Nibbleblog 4.0.3, subida CVE-2015-6967, sudo | [ES](machines/linux/nibbles/README.md) | [Ver](machines/linux/nibbles/README.en.md) |
| Doctor | Linux | Easy | Web / Infraestructura | Retired (ref.) | SSTI con Jinja2 en un vhost, Splunk 8.0.x | [ES](machines/linux/doctor/README.md) | [Ver](machines/linux/doctor/README.en.md) |
| Poison | FreeBSD | Medium | Web / Unix | Retired (ref.) | LFI en `browse.php`, base64 en `pwdbackup.txt`, VNC como root con `secret.zip` | [ES](machines/freebsd/poison/README.md) | [Ver](machines/freebsd/poison/README.en.md) |
| SolidState | Linux | Medium | Servicios | Retired (ref.) | Apache James con credenciales por defecto, cron escribible | [ES](machines/linux/solidstate/README.md) | [Ver](machines/linux/solidstate/README.en.md) |
| DevOops | Linux | Medium | Web / Desarrollo | Retired (ref.) | XXE en la subida de XML y clave de root en el historial de git | [ES](machines/linux/devoops/README.md) | [Ver](machines/linux/devoops/README.en.md) |
| Pirate | Windows | Hard | Active Directory | Retired (ref.) | Pre-Windows 2000, gMSA, RBCD, S4U2Proxy | [ES](machines/windows/pirate/README.md) | [Ver](machines/windows/pirate/README.en.md) |
| MonitorsFour | Windows | Easy | Web / Contenedores | Retired (ref.) | IDOR en la API, MD5 crackeado, CVE-2025-24367 en Cacti, escape por la API de Docker | [ES](machines/windows/monitorsfour/README.md) | [Ver](machines/windows/monitorsfour/README.en.md) |
| Pterodactyl | Linux | Medium | Web / Linux | Retired (ref.) | CVE-2025-49132 en `/locales`, PEAR `pearcmd`, cadena CVE-2025-6018/6019 | [ES](machines/linux/pterodactyl/README.md) | [Ver](machines/linux/pterodactyl/README.en.md) |
| Frolic | Linux | Easy | Web / Linux | Retired (ref.) | Client-side login check, PlaySMS 1.4 CSV upload and a SUID `rop` with ret2libc | [ES](machines/linux/frolic/README.md) | [Ver](machines/linux/frolic/README.en.md) |
| Sea | Linux | Easy | Web / Linux | Retired (ref.) | WonderCMS CVE-2023-41425, cracked bcrypt hash and command injection on 8080 | [ES](machines/linux/sea/README.md) | [Ver](machines/linux/sea/README.en.md) |
| Devel | Windows | Easy | Windows / Web | Retired (ref.) | Writable anonymous FTP over IIS, ASPX webshell and MS10-015 or `SeImpersonate` | [ES](machines/windows/devel/README.md) | [Ver](machines/windows/devel/README.en.md) |
| Fluffy | Windows | Easy | Active Directory | Retired (ref.) | CVE-2025-24071 NTLM theft, shadow credentials and ADCS ESC16 | [ES](machines/windows/fluffy/README.md) | [Ver](machines/windows/fluffy/README.en.md) |
| Garfield | Windows | Hard | Active Directory | Retired (ref.) | RODC, KeyList golden ticket, DC dump and pass-the-hash | [ES](machines/windows/garfield/README.md) | [Ver](machines/windows/garfield/README.en.md) |
| Buff | Windows | Easy | Web | Retired (ref.) | Subida sin autenticacion, CloudMe 1.11.2 | [ES](machines/windows/buff/README.md) | [Ver](machines/windows/buff/README.en.md) |
| Blackfield | Windows | Hard | Active Directory | Retired (ref.) | AS-REP, volcado de lsass, SeBackupPrivilege, NTDS | [ES](machines/windows/blackfield/README.md) | [Ver](machines/windows/blackfield/README.en.md) |
| Explosion | Windows | Very Easy | Starting Point | Available | RDP with a passwordless `Administrator` account | [ES](machines/starting-point/explosion/README.md) | [Ver](machines/starting-point/explosion/README.en.md) |
| Preignition | Linux | Very Easy | Starting Point | Available | Hidden `/admin.php` panel with `admin:admin` | [ES](machines/starting-point/preignition/README.md) | [Ver](machines/starting-point/preignition/README.en.md) |
| Mongod | Linux | Very Easy | Starting Point | Available | MongoDB on 27017 with no authentication | [ES](machines/starting-point/mongod/README.md) | [Ver](machines/starting-point/mongod/README.en.md) |
| Synced | Linux | Very Easy | Starting Point | Available | Anonymous rsync on 873 | [ES](machines/starting-point/synced/README.md) | [Ver](machines/starting-point/synced/README.en.md) |
| Sequel | Linux | Very Easy | Starting Point | Available | MySQL with a passwordless `root` | [ES](machines/starting-point/sequel/README.md) | [Ver](machines/starting-point/sequel/README.en.md) |
| Appointment | Linux | Very Easy | Starting Point | Available | Login SQLi: `admin' or '1'='1'#` | [ES](machines/starting-point/appointment/README.md) | [Ver](machines/starting-point/appointment/README.en.md) |
| Crocodile | Linux | Very Easy | Starting Point | Available | Anonymous FTP with `allowed.userlist` and `.passwd` | [ES](machines/starting-point/crocodile/README.md) | [Ver](machines/starting-point/crocodile/README.en.md) |
| Responder | Windows | Very Easy | Starting Point | Available | LFI to UNC, NetNTLMv2 capture and WinRM | [ES](machines/starting-point/responder/README.md) | [Ver](machines/starting-point/responder/README.en.md) |
| Three | Linux | Very Easy | Starting Point | Available | Unauthenticated S3 bucket and webshell | [ES](machines/starting-point/three/README.md) | [Ver](machines/starting-point/three/README.en.md) |
| Ignition | Linux | Very Easy | Starting Point | Available | Magento with `admin:qwerty123` on `/admin` | [ES](machines/starting-point/ignition/README.md) | [Ver](machines/starting-point/ignition/README.en.md) |
| Bike | Linux | Very Easy | Starting Point | Available | Handlebars SSTI in Node.js up to root | [ES](machines/starting-point/bike/README.md) | [Ver](machines/starting-point/bike/README.en.md) |
| Funnel | Linux | Very Easy | Starting Point | Available | SSH spray and a tunnel to loopback PostgreSQL | [ES](machines/starting-point/funnel/README.md) | [Ver](machines/starting-point/funnel/README.en.md) |
| Pennyworth | Linux | Very Easy | Starting Point | Available | Jenkins `root:password` and the Groovy console | [ES](machines/starting-point/pennyworth/README.md) | [Ver](machines/starting-point/pennyworth/README.en.md) |
| Tactics | Windows | Very Easy | Starting Point | Available | SMB null session and a passwordless `Administrator` | [ES](machines/starting-point/tactics/README.md) | [Ver](machines/starting-point/tactics/README.en.md) |
| Archetype | Windows | Very Easy | Starting Point | Available | `prod.dtsConfig`, `xp_cmdshell`, PS history and psexec | [ES](machines/starting-point/archetype/README.md) | [Ver](machines/starting-point/archetype/README.en.md) |
| Oopsie | Linux | Very Easy | Starting Point | Available | Cookie IDOR, webshell upload and the `bugtracker` SUID | [ES](machines/starting-point/oopsie/README.md) | [Ver](machines/starting-point/oopsie/README.en.md) |
| Vaccine | Linux | Very Easy | Starting Point | Available | `backup.zip`, SQLi with `sqlmap --os-shell` and `sudo vi` | [ES](machines/starting-point/vaccine/README.md) | [Ver](machines/starting-point/vaccine/README.en.md) |
| Unified | Linux | Very Easy | Starting Point | Available | Log4Shell (CVE-2021-44228) on UniFi and MongoDB 27117 | [ES](machines/starting-point/unified/README.md) | [Ver](machines/starting-point/unified/README.en.md) |
| Included | Linux | Very Easy | Starting Point | Available | LFI to `/proc/net/udp`, unauthenticated TFTP and `lxd` | [ES](machines/starting-point/included/README.md) | [Ver](machines/starting-point/included/README.en.md) |
| Markup | Windows | Very Easy | Starting Point | Available | XXE to read `id_rsa` and a scheduled `job.bat` | [ES](machines/starting-point/markup/README.md) | [Ver](machines/starting-point/markup/README.en.md) |
| Base | Linux | Very Easy | Starting Point | Available | `strcmp` with arrays, unrestricted upload and `sudo find` | [ES](machines/starting-point/base/README.md) | [Ver](machines/starting-point/base/README.en.md) |
| Cap | Linux | Easy | Machines | Retired | IDOR, pcap analysis, `cap_setuid` | [ES](machines/linux/cap/README.md) | [Ver](machines/linux/cap/README.en.md) |
| MakeSense | Linux | Medium | Season 11 | Retired | Admin-bot XSS, forged AES-GCM, malicious plugin, OCR as root | [ES](machines/linux/makesense/README.md) | [Ver](machines/linux/makesense/README.en.md) |
| Armageddon | Linux | Easy | Machines | **Retired** (ref.) | Drupal 7.56, Drupalgeddon2, snap hook with `sudo` | [ES](machines/linux/armageddon/README.md) | [Ver](machines/linux/armageddon/README.en.md) |
| Bashed | Linux | Easy | Machines | **Retired** (ref.) | `phpbash` web shell, `sudo -u scriptmanager`, root cron | [ES](machines/linux/bashed/README.md) | [Ver](machines/linux/bashed/README.en.md) |
| Bastion | Windows | Easy | Machines | **Retired** (ref.) | SMB backup with VHDX, SAM/SYSTEM, mRemoteNG | [ES](machines/windows/bastion/README.md) | [Ver](machines/windows/bastion/README.en.md) |
| Beep | Linux | Easy | Machines | **Retired** (ref.) | Elastix LFI, CVE-2012-4869, interactive `nmap` | [ES](machines/linux/beep/README.md) | [Ver](machines/linux/beep/README.en.md) |
| Blocky | Linux | Easy | Machines | **Retired** (ref.) | credentials in a JAR, reuse, `sudo ALL` | [ES](machines/linux/blocky/README.md) | [Ver](machines/linux/blocky/README.en.md) |
| Blunder | Linux | Easy | Machines | **Retired** (ref.) | Bludit, brute-force bypass, `sudo -u#-1` | [ES](machines/linux/blunder/README.md) | [Ver](machines/linux/blunder/README.en.md) |
| Bounty | Windows | Easy | Machines | **Retired** (ref.) | `web.config` on IIS, `SeImpersonate`, JuicyPotato | [ES](machines/windows/bounty/README.md) | [Ver](machines/windows/bounty/README.en.md) |
| Delivery | Linux | Easy | Machines | **Retired** (ref.) | osTicket + Mattermost, bcrypt with rules | [ES](machines/linux/delivery/README.md) | [Ver](machines/linux/delivery/README.en.md) |
| Facts | Linux | Easy | Machines | **Retired** (ref.) | Camaleon CMS, MinIO, SSH key, `facter` | [ES](machines/linux/facts/README.md) | [Ver](machines/linux/facts/README.en.md) |
| Forest | Windows | Easy | Machines | **Retired** (ref.) | AS-REP, `Account Operators` to Exchange, DCSync | [ES](machines/windows/forest/README.md) | [Ver](machines/windows/forest/README.en.md) |
| FriendZone | Linux | Easy | Machines | **Retired** (ref.) | AXFR, LFI + SMB, `os.py` hijack | [ES](machines/linux/friendzone/README.md) | [Ver](machines/linux/friendzone/README.en.md) |
| Admirer | Linux | Easy | Machines | **Retired** (ref.) | Adminer 4.6.2 with a rogue MySQL and `PYTHONPATH` inherited through sudo | [ES](machines/linux/admirer/README.md) | [Ver](machines/linux/admirer/README.en.md) |
| Arctic | Windows | Easy | Machines | **Retired** (ref.) | ColdFusion 8 + FCKeditor, `SeImpersonate`, JuicyPotato | [ES](machines/windows/arctic/README.md) | [Ver](machines/windows/arctic/README.en.md) |
| Bank | Linux | Easy | Machines | **Retired** (ref.) | AXFR, `302` to `200`, `.htb` whitelist, `emergency` SUID | [ES](machines/linux/bank/README.md) | [Ver](machines/linux/bank/README.en.md) |
| Blue | Windows | Easy | Machines | **Retired** (ref.) | MS17-010 EternalBlue, `hashdump` | [ES](machines/windows/blue/README.md) | [Ver](machines/windows/blue/README.en.md) |
| Cronos | Linux | Medium | Machines | **Retired** (ref.) | AXFR, SQLi, command injection, root cron over `artisan` | [ES](machines/linux/cronos/README.md) | [Ver](machines/linux/cronos/README.en.md) |
| PingPong | Windows | Insane | Machines | Retired | Dual AD forest, ESC13, pivot, gMSA, JEA, RBCD and ESC4→ESC1 | [ES](machines/windows/pingpong/README.md) | [Ver](machines/windows/pingpong/README.en.md) |
| AirTouch | Linux | Medium | Machines | **Retired** (ref.) | WPA2 handshake, PEAP-MSCHAPv2 Evil Twin and VPN pivot | [ES](machines/linux/airtouch/README.md) | [Ver](machines/linux/airtouch/README.en.md) |
| Eighteen | Windows | Hard | Machines | **Retired** (ref.) | MSSQL `IMPERSONATE`, Werkzeug hash, CVE-2025-53779 (dMSA) | [ES](machines/windows/eighteen/README.md) | [Ver](machines/windows/eighteen/README.en.md) |
| Sink | Linux | Insane | Machines | **Retired** (ref.) | CL.TE smuggling, Gitea with AWS keys, Secrets Manager and KMS | [ES](machines/linux/sink/README.md) | [Ver](machines/linux/sink/README.en.md) |
| Sorcery | Linux | Insane | Machines | **Retired** (ref.) | Cypher injection, passkey XSS, Kafka and FreeIPA | [ES](machines/linux/sorcery/README.md) | [Ver](machines/linux/sorcery/README.en.md) |
| Cobblestone | Linux | Insane | Machines | **Retired** (ref.) | Second-order SQLi, XSS, Twig SSTI and CVE-2024-47533 | [ES](machines/linux/cobblestone/README.md) | [Ver](machines/linux/cobblestone/README.en.md) |
| Code | Linux | Easy | Machines | **Retired** (ref.) | Python blocklist escape, bcrypt and `backy.sh` traversal | [ES](machines/linux/code/README.md) | [Ver](machines/linux/code/README.en.md) |
| Kobold | Linux | Easy | Machines | **Retired** (ref.) | MCPJam Inspector CVE-2026-23744, PrivateBin and privileged container | [ES](machines/linux/kobold/README.md) | [Ver](machines/linux/kobold/README.en.md) |
| Helix | Linux | Medium | Machines | **Retired** (ref.) | NiFi 1.21.0, H2 `CREATE ALIAS` (CVE-2023-34468) and OPC UA | [ES](machines/linux/helix/README.md) | [Ver](machines/linux/helix/README.en.md) |
| Interpreter | Linux | Medium | Machines | **Retired** (ref.) | Mirth Connect CVE-2023-43208, PBKDF2 and `eval()` in a local service | [ES](machines/linux/interpreter/README.md) | [Ver](machines/linux/interpreter/README.en.md) |
| VariaType | Linux | Medium | Machines | **Retired** (ref.) | fontTools CVE-2025-66034, FontForge CVE-2024-25082, setuptools CVE-2025-47273 | [ES](machines/linux/variatype/README.md) | [Ver](machines/linux/variatype/README.en.md) |
| Academy | Linux | Easy | Web / Linux | Retired (ref.) | Roleid → Laravel CVE-2018-15133 via `APP_KEY`, `.env` and `composer` under sudo | [ES](machines/linux/academy/README.md) | [Ver](machines/linux/academy/README.en.md) |
| Active | Windows | Easy | Active Directory | Retired (ref.) | GPP in SYSVOL, `gpp-decrypt`, Kerberoasting `Administrator` | [ES](machines/windows/active/README.md) | [Ver](machines/windows/active/README.en.md) |
| Apocalyst | Linux | Medium | Web / Linux | Retired (ref.) | WordPress, `cewl` and `steghide`, hydra, PHP plugin and a writable `/etc/passwd` | [ES](machines/linux/apocalyst/README.md) | [Ver](machines/linux/apocalyst/README.en.md) |
| OpenAdmin | Linux | Easy | Web / Linux | Retired (ref.) | OpenNetAdmin 18.1.1, credential reuse, `ssh2john` and a `nano` escape | [ES](machines/linux/openadmin/README.md) | [Ver](machines/linux/openadmin/README.en.md) |
| Tabby | Linux | Easy | Web / Linux | Retired (ref.) | LFI to `tomcat-users.xml`, WAR via `manager/text`, `fcrackzip` and the `lxd` group | [ES](machines/linux/tabby/README.md) | [Ver](machines/linux/tabby/README.en.md) |
| Jerry | Windows | Easy | Web / Windows | Retired (ref.) | Tomcat 7 with default credentials, WAR via `/manager/text` and a direct SYSTEM shell | [ES](machines/windows/jerry/README.md) | [Ver](machines/windows/jerry/README.en.md) |
| Chatterbox | Windows | Medium | Servicios / Windows | Retired (ref.) | AChat 0.150 buffer overflow (EDB 36025) and AutoLogon credentials in the registry | [ES](machines/windows/chatterbox/README.md) | [Ver](machines/windows/chatterbox/README.en.md) |
| Heist | Windows | Easy | Web / Windows | Retired (ref.) | Cisco config with type 7 and type 5, WinRM spray and `procdump` on Firefox | [ES](machines/windows/heist/README.md) | [Ver](machines/windows/heist/README.en.md) |
| Valentine | Linux | Easy | Web / Linux | Retired (ref.) | Heartbleed leaks an RSA key passphrase, SSH and a root `tmux` socket | [ES](machines/linux/valentine/README.md) | [Ver](machines/linux/valentine/README.en.md) |
| Shocker | Linux | Easy | Web / Linux | Retired (ref.) | Shellshock in a CGI (`user.sh`) and `sudo perl` via GTFOBins | [ES](machines/linux/shocker/README.md) | [Ver](machines/linux/shocker/README.en.md) |
| SwagShop | Linux | Easy | Web / Linux | Retired (ref.) | Magento with the Shoplift SQLi, Connect Manager and `sudo vi` | [ES](machines/linux/swagshop/README.md) | [Ver](machines/linux/swagshop/README.en.md) |
| Networked | Linux | Easy | Web / Linux | Retired (ref.) | Source-code backup, double extension, injectable cron and unquoted `changename.sh` that `source`s the ifcfg | [ES](machines/linux/networked/README.md) | [Ver](machines/linux/networked/README.en.md) |
| Sense | FreeBSD | Easy | Infraestructura / FreeBSD | Retired (ref.) | pfSense 2.1.3 with default credentials and CVE-2014-4688 as root | [ES](machines/freebsd/sense/README.md) | [Ver](machines/freebsd/sense/README.en.md) |
| Legacy | Windows | Easy | Windows / SMB | Retired (ref.) | MS08-067 over SMBv1 on Windows XP | [ES](machines/windows/legacy/README.md) | [Ver](machines/windows/legacy/README.en.md) |
| Sunday | Solaris | Easy | Servicios / Solaris | Retired (ref.) | `finger` user enumeration, cracked shadow and `sudo wget` | [ES](machines/solaris/sunday/README.md) | [Ver](machines/solaris/sunday/README.en.md) |
| Lame | Linux | Easy | SMB / servicios antiguos | Retired (ref.) | Samba `usermap_script` (CVE-2007-2447) for direct root; `distcc` and `vsftpd` as alternates | [ES](machines/linux/lame/README.md) | [Ver](machines/linux/lame/README.en.md) |
| Optimum | Windows | Easy | Web / Windows | Retired (ref.) | Rejetto HFS 2.3 (CVE-2014-6287) and MS16-032 up to SYSTEM | [ES](machines/windows/optimum/README.md) | [Ver](machines/windows/optimum/README.en.md) |
| Sau | Linux | Easy | Web / SSRF | Retired (ref.) | Request Baskets SSRF into Maltrail, then `sudo systemctl` pager escape | [ES](machines/linux/sau/README.md) | [Ver](machines/linux/sau/README.en.md) |
| Nineveh | Linux | Medium | Web / Enumeración | Retired (ref.) | phpLiteAdmin + LFI, port knocking and chkrootkit 0.49 as root | [ES](machines/linux/nineveh/README.md) | [Ver](machines/linux/nineveh/README.en.md) |
| Jeeves | Windows | Medium | Windows / Credenciales | Retired (ref.) | Unauthenticated Jenkins, KeePass, pass-the-hash and a flag in an NTFS stream | [ES](machines/windows/jeeves/README.md) | [Ver](machines/windows/jeeves/README.en.md) |
| CozyHosting | Linux | Easy | Web / Spring Boot | Retired (ref.) | Actuator session leak, panel command injection, PostgreSQL and `sudo ssh` | [ES](machines/linux/cozyhosting/README.md) | [Ver](machines/linux/cozyhosting/README.en.md) |
| BoardLight | Linux | Easy | Web / CMS | Retired (ref.) | Dolibarr 17.0.0 with defaults, CVE-2023-30253 and an Enlightenment SUID | [ES](machines/linux/boardlight/README.md) | [Ver](machines/linux/boardlight/README.en.md) |
| Busqueda | Linux | Easy | Web / Inyección | Retired (ref.) | Searchor `eval()`, a `.git` with credentials, Gitea and the relative `full-checkup.sh` | [ES](machines/linux/busqueda/README.md) | [Ver](machines/linux/busqueda/README.en.md) |
| Soccer | Linux | Easy | Web / SQLi en WebSocket | Retired (ref.) | Default Tiny File Manager, blind WebSocket SQLi and `doas` with `dstat` | [ES](machines/linux/soccer/README.md) | [Ver](machines/linux/soccer/README.en.md) |
| Timelapse | Windows | Easy | Active Directory / Certificados | Retired (ref.) | Anonymous SMB, PFX, PowerShell history and LAPS up to Administrator | [ES](machines/windows/timelapse/README.md) | [Ver](machines/windows/timelapse/README.en.md) |
| Cicada | Windows | Easy | Active Directory / SMB | Retired (ref.) | Guest SMB, onboarding password, spray, `description` and `info`, `SeBackupPrivilege` and SAM/SYSTEM | [ES](machines/windows/cicada/README.md) | [Ver](machines/windows/cicada/README.en.md) |
| Support | Windows | Easy | Active Directory | Retired (ref.) | Reversing `UserInfo.exe` (XOR + base64), LDAP, password in `info`, GenericAll over the DC and RBCD | [ES](machines/windows/support/README.md) | [Ver](machines/windows/support/README.en.md) |
| Administrator | Windows | Medium | Active Directory | Retired (ref.) | GenericAll and ForceChangePassword, FTP with `.psafe3`, GenericWrite, targeted kerberoasting and DCSync | [ES](machines/windows/administrator/README.md) | [Ver](machines/windows/administrator/README.en.md) |
| Escape | Windows | Medium | Active Directory / MSSQL | Retired (ref.) | PDF with credentials, `xp_dirtree` as `sql_svc`, `ERRORLOG.BAK` and ADCS ESC1 up to Administrator | [ES](machines/windows/escape/README.md) | [Ver](machines/windows/escape/README.en.md) |
| Pilgrimage | Linux | Easy | Web / Linux | Retired (ref.) | Exposed `/.git`, ImageMagick 7.1.0-49 (CVE-2022-44268) and binwalk 2.3.2 (CVE-2022-4510) | [ES](machines/linux/pilgrimage/README.md) | [Ver](machines/linux/pilgrimage/README.en.md) |
| Sauna | Windows | Easy | Active Directory | Retired (ref.) | AS-REP roasting, autologon credentials and DCSync | [ES](machines/windows/sauna/README.md) | [Ver](machines/windows/sauna/README.en.md) |
| Netmon | Windows | Easy | Web / Windows | Retired (ref.) | Anonymous FTP, PRTG and CVE-2018-9276 | [ES](machines/windows/netmon/README.md) | [Ver](machines/windows/netmon/README.en.md) |
| Servmon | Windows | Easy | Windows / Services | Retired (ref.) | NVMS path traversal, NSClient++ and SSH tunnel | [ES](machines/windows/servmon/README.md) | [Ver](machines/windows/servmon/README.en.md) |
| Resolute | Windows | Medium | Active Directory | Retired (ref.) | Anonymous LDAP, password reuse and `DnsAdmins` | [ES](machines/windows/resolute/README.md) | [Ver](machines/windows/resolute/README.en.md) |
| Bastard | Windows | Medium | Web / Windows | Retired (ref.) | Drupalgeddon2 and JuicyPotato | [ES](machines/windows/bastard/README.md) | [Ver](machines/windows/bastard/README.en.md) |
| Cascade | Windows | Medium | Active Directory / Windows | Retired (ref.) | Anonymous LDAP, `cascadeLegacyPwd`, reversible VNC and AD Recycle Bin | [ES](machines/windows/cascade/README.md) | [Ver](machines/windows/cascade/README.en.md) |
| Traceback | Linux | Easy | Web / Linux | Retired (ref.) | SmEvK web shell with default credentials, `luvit` via sudo and writable MOTD | [ES](machines/linux/traceback/README.md) | [Ver](machines/linux/traceback/README.en.md) |
| Craft | Linux | Easy | Web / Linux | Retired (ref.) | `eval()` in Flask, Gogs history, cleartext MySQL and a Vault OTP | [ES](machines/linux/craft/README.md) | [Ver](machines/linux/craft/README.en.md) |
| Book | Linux | Medium | Web / Linux | Retired (ref.) | SQL truncation on signup, XSS in the PDF and a `logrotate` race | [ES](machines/linux/book/README.md) | [Ver](machines/linux/book/README.en.md) |
| Querier | Windows | Medium | Active Directory / MSSQL | Retired (ref.) | Credentials in a macro, `xp_dirtree`, NetNTLMv2 and GPP | [ES](machines/windows/querier/README.md) | [Ver](machines/windows/querier/README.en.md) |
| Remote | Windows | Medium | Web / Windows | Retired (ref.) | NFS with the Umbraco backup, SHA1, XSLT RCE and TeamViewer | [ES](machines/windows/remote/README.md) | [Ver](machines/windows/remote/README.en.md) |
| Luke | FreeBSD | Medium | Web / FreeBSD | Retired (ref.) | Cleartext `config.php`, an API with JWT and Ajenti as root | [ES](machines/freebsd/luke/README.md) | [Ver](machines/freebsd/luke/README.en.md) |

> **States:** **Available** = Starting Point, always available and publishable · **Retired** = retired, publishable · **Active** = in its season, not published until HTB retires it · **ref.** = reference notes, not played on this profile.
>
> Reference catalogue: [machines/catalog.en.md](machines/catalog.en.md) · [ES](machines/catalog.md).

### 🏅 Verifiable achievements

Machines completed on this profile have their public link here. Rows marked `ref.` are absent: they are study notes, with no achievement of your own to link.

| Machine | Achievement |
|---|---|
| Meow | https://labs.hackthebox.com/achievement/machine/4187928/394 |
| Fawn | https://labs.hackthebox.com/achievement/machine/4187928/393 |
| Dancing | https://labs.hackthebox.com/achievement/machine/4187928/395 |
| Redeemer | https://labs.hackthebox.com/achievement/machine/4187928/472 |
| Cap | https://labs.hackthebox.com/achievement/machine/4187928/351 |
| MakeSense | https://labs.hackthebox.com/achievement/machine/4187928/918 |
| DutyBound | https://labs.hackthebox.com/achievement/machine/4187928/999 |
| Stream | https://labs.hackthebox.com/achievement/machine/4187928/990 |
| Layover | https://labs.hackthebox.com/achievement/machine/4187928/984 |
| Connected | https://labs.hackthebox.com/achievement/machine/4187928/906 |
| Unclaimed | https://labs.hackthebox.com/achievement/machine/4187928/1012 |
| PingPong | https://labs.hackthebox.com/achievement/machine/4187928/891 |

- **Retired:** publishable writeup.
- **Active:** private draft only; published once HTB retires the machine.

---

## 🧩 Challenges

Solved challenges. There is no privilege escalation: the goal is the challenge flag, so the writeup focuses on the bug and the exploitation chain.

| Challenge | Type | Difficulty | State | Key techniques | ES | EN |
|---|---|---|---|---|---|---|
| Marshal in the Middle | Forensics | Medium | **Retired** | Zeek logs, TLS decryption and HTTP exfiltration | [ES](challenges/Marshal%20in%20the%20Middle/README.md) | [Ver](challenges/Marshal%20in%20the%20Middle/README.en.md) |
| Lernaean | Web | Easy | **Retired** | Hydra, weak password and avoidable JavaScript redirect | [ES](challenges/Lernaean/README.md) | [Ver](challenges/Lernaean/README.en.md) |
| Kryptor | Pwn | Insane | **Retired** | Kernel 5.9.10: DirtyPipe (CVE-2022-0847) over busybox's entry point, triggered through `modprobe` | [ES](challenges/Kryptor/README.md) | [Ver](challenges/Kryptor/README.en.md) |
| Oldbridge | Pwn | Medium | **Retired** | Canary brute force (`fork`), PIE leak and `leave; ret` pivot into ret2libc | [ES](challenges/Oldbridge/README.md) | [Ver](challenges/Oldbridge/README.en.md) |
| Space Pirate: Entrypoint | Pwn | Very Easy | **Retired** | Format string in `printf(local_38)`: `%7$hn` turns `0xdeadbeef` into `0xdead1337` | [ES](challenges/Space%20Pirate%20Entrypoint/README.md) | [Ver](challenges/Space%20Pirate%20Entrypoint/README.en.md) |
| Space Pirate: Going Deeper | Pwn | Very Easy | **Retired** | One-byte overflow with no PIE: 56 filler bytes and `\x01` over the return address | [ES](challenges/Space%20Pirate%20Going%20Deeper/README.md) | [Ver](challenges/Space%20Pirate%20Going%20Deeper/README.en.md) |
| Vault-breaker | Pwn | Very Easy | **Retired** | `strcpy` truncates the key at the first null; lengths 31→0 leave the XOR at zero | [ES](challenges/Vault-breaker/README.md) | [Ver](challenges/Vault-breaker/README.en.md) |
| ropme | Pwn | Hard | **Retired** | Ret2libc with a `puts@got` leak: libc base and `system("/bin/sh")` | [ES](challenges/ropme/README.md) | [Ver](challenges/ropme/README.en.md) |
| Easy Phish | OSINT | Very Easy | **Retired** | `?all` SPF and `p=none` DMARC on the legitimate domain | [ES](challenges/Easy%20Phish/README.md) | [Ver](challenges/Easy%20Phish/README.en.md) |
| Hidden in Colors | Stego | Hard | **Retired** | PNG hex colours: the data lives in the colour value, not the LSB | [ES](challenges/Hidden%20in%20Colors/README.md) | [Ver](challenges/Hidden%20in%20Colors/README.en.md) |
| Bare Metal | Hardware | Easy | **Retired** | 3.3 V UART, U-Boot and rootfs extraction with `binwalk` | [ES](challenges/Bare%20Metal/README.md) | [Ver](challenges/Bare%20Metal/README.en.md) |
| Cryptohorrific | Mobile | Easy | **Retired** | iOS app: base64 blob in the plist, AES key inside the Mach-O binary | [ES](challenges/Cryptohorrific/README.md) | [Ver](challenges/Cryptohorrific/README.en.md) |
| Dark Embargo | Web / Pwn | Medium | **Retired** | PHP 8.4.26: OOM in `session.upload_progress`, use-after-free, ASLR leak via `Set-Cookie`, `pDestructor` → `system()` | [ES](challenges/Dark%20Embargo/README.md) | [Ver](challenges/Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | **Retired** | MD5 against the clock: session handling, regex, hashing in a script | [ES](challenges/Emdee%20five%20for%20life/README.md) | [Ver](challenges/Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | **Retired** | Blind LDAP injection: the flag is `reese`'s password, not the `*` bypass | [ES](challenges/Phonebook/README.md) | [Ver](challenges/Phonebook/README.en.md) |
| Under Construction | Web | Easy | **Retired** | JWT `alg` confusion RS256→HS256 signing with `/public.pem` | [ES](challenges/Under%20Construction/README.md) | [Ver](challenges/Under%20Construction/README.en.md) |
| Toxic | Web | Very Easy | Retired | PHP deserialization in the cookie → `PageModel::__destruct` → LFI plus log poisoning | [ES](challenges/Toxic/README.md) | [Ver](challenges/Toxic/README.en.md) |
| LoveTok | Web | Easy | **Retired** | `eval` over the date format; `addslashes` does not stop `${}` | [ES](challenges/LoveTok/README.md) | [Ver](challenges/LoveTok/README.en.md) |
| Templated | Web | Easy | Retired | Jinja2 SSTI at `/<nombre>`: `{{7*7}}` → 49 and RCE via `__globals__` | [ES](challenges/Templated/README.md) | [Ver](challenges/Templated/README.en.md) |
| baby ninja jinja | Web | Easy | Retired | SSTI con blacklist: `{%print%}`, filtro `attr` y `replace` | [ES](challenges/baby%20ninja%20jinja/README.md) | [Ver](challenges/baby%20ninja%20jinja/README.en.md) |
| Spookifier | Web | Very Easy | Retired | Mako SSTI through `font4`: `${self.module.cache.util.os.popen(...).read()}` | [ES](challenges/Spookifier/README.md) | [Ver](challenges/Spookifier/README.en.md) |
| Flag Command | Web | Very Easy | Retired | Bundle JS con endpoints ocultos; comando secreto por API | [ES](challenges/Flag%20Command/README.md) | [Ver](challenges/Flag%20Command/README.en.md) |
| Labyrinth Linguist | Web | Easy | **Retired** | Velocity SSTI: `#set` plus Java reflection | [ES](challenges/Labyrinth%20Linguist/README.md) | [Ver](challenges/Labyrinth%20Linguist/README.en.md) |
| breaking grad | Web | Easy | Retired | Contaminación de prototipos en Node hasta `child_process` | [ES](challenges/breaking%20grad/README.md) | [Ver](challenges/breaking%20grad/README.en.md) |
| Weather App | Web | Easy | **Retired** | SSRF with *response splitting* and SQLi in the internal service up to admin account takeover | [ES](challenges/Weather%20App/README.md) | [Ver](challenges/Weather%20App/README.en.md) |
| Freelancer | Web | Easy | **Retired** | SQLi in `portfolio.php?id=` and an `/admin` panel found by fuzzing | [ES](challenges/Freelancer/README.md) | [Ver](challenges/Freelancer/README.en.md) |
| Passman | Web | Easy | **Retired** | GraphQL: unauthenticated `UpdatePassword`; the flag lives in the admin's manager | [ES](challenges/Passman/README.md) | [Ver](challenges/Passman/README.en.md) |
| Cartographer | Web | Easy | **Retired** | SQLi in the login form and `panel.php?info=flag` | [ES](challenges/Cartographer/README.md) | [Ver](challenges/Cartographer/README.en.md) |
| Dynastic | Crypto | Very Easy | **Retired** | Trithemius cipher: the shift is the index | [ES](challenges/Dynastic/README.md) | [Ver](challenges/Dynastic/README.en.md) |
| Makeshift | Crypto | Very Easy | **Retired** | Reversal plus permutation of three-byte blocks | [ES](challenges/Makeshift/README.md) | [Ver](challenges/Makeshift/README.en.md) |
| Primary Knowledge | Crypto | Very Easy | **Retired** | RSA with a prime `n`: `φ(n) = n − 1`, no factorisation needed | [ES](challenges/Primary%20Knowledge/README.md) | [Ver](challenges/Primary%20Knowledge/README.en.md) |
| Iced Tea | Crypto | Easy | **Retired** | 32-round TEA with `delta` and a 32-bit mask | [ES](challenges/Iced%20Tea/README.md) | [Ver](challenges/Iced%20Tea/README.en.md) |
| Illumination | Forensics | Easy | **Retired** | Leaked `.git`: the token survives in history, base64-encoded | [ES](challenges/Illumination/README.md) | [Ver](challenges/Illumination/README.en.md) |
| MarketDump | Forensics | Easy | **Retired** | Export HTTP objects and decode the outlier as base58 | [ES](challenges/MarketDump/README.md) | [Ver](challenges/MarketDump/README.en.md) |
| Took the Byte | Forensics | Easy | **Retired** | Single-byte XOR (`0xFF`) over `password` → a ZIP with `password.txt` | [ES](challenges/Took%20the%20Byte/README.md) | [Ver](challenges/Took%20the%20Byte/README.en.md) |
| Deadly Arthropod | Forensics | Medium | **Retired** | Rebuild keystrokes from USB keyboard HID reports | [ES](challenges/Deadly%20Arthropod/README.md) | [Ver](challenges/Deadly%20Arthropod/README.en.md) |
| Obscure | Forensics | Easy | **Retired** | Obfuscated webshell, PCAP with commands and a `.kdbx` cracked with john | [ES](challenges/Obscure/README.md) | [Ver](challenges/Obscure/README.en.md) |
| Keep Tryin' | Forensics | Medium | **Retired** | DNS exfiltration in base64url and RC4 with a weak key | [ES](challenges/Keep%20Tryin'/README.md) | [Ver](challenges/Keep%20Tryin'/README.en.md) |
| Alien Cradle | Forensics | Very Easy | **Retired** | Deobfuscate a PowerShell download cradle built from string concatenation | [ES](challenges/Alien%20Cradle/README.md) | [Ver](challenges/Alien%20Cradle/README.en.md) |
| Extraterrestrial Persistence | Forensics | Very Easy | **Retired** | base64-encoded systemd unit as the persistence mechanism | [ES](challenges/Extraterrestrial%20Persistence/README.md) | [Ver](challenges/Extraterrestrial%20Persistence/README.en.md) |
| Plaintext Tleasure | Forensics | Very Easy | **Retired** | PCAP with cleartext HTTP: credentials and transfer readable without decryption | [ES](challenges/Plaintext%20Tleasure/README.md) | [Ver](challenges/Plaintext%20Tleasure/README.en.md) |
| Urgent | Forensics | Very Easy | **Retired** | Phishing `.eml`: base64/quoted-printable MIME, URL encoding and a VBS attachment | [ES](challenges/Urgent/README.md) | [Ver](challenges/Urgent/README.en.md) |
| BabyEncryption | Crypto | Very Easy | **Retired** | Affine map modulo 256 and the modular inverse | [ES](challenges/BabyEncryption/README.md) | [Ver](challenges/BabyEncryption/README.en.md) |
| Ancient Encodings | Crypto | Very Easy | **Retired** | Base64 inside hexadecimal, no key | [ES](challenges/Ancient%20Encodings/README.md) | [Ver](challenges/Ancient%20Encodings/README.en.md) |
| SpookyPass | Reversing | Very Easy | **Retired** | ELF with the password and flag in `.rodata`; the flag as UTF-32 (`strings -e l`) | [ES](challenges/SpookyPass/README.md) | [Ver](challenges/SpookyPass/README.en.md) |
| KORP Terminal | Web | Very Easy | **Retired** | Error-based SQLi and a cracked bcrypt hash | [ES](challenges/KORP%20Terminal/README.md) | [Ver](challenges/KORP%20Terminal/README.en.md) |
| TimeKORP | Web | Very Easy | **Retired** | Command injection into `date` through `format`: `%H:%M:%S' \|cat /flag #` | [ES](challenges/TimeKORP/README.md) | [Ver](challenges/TimeKORP/README.en.md) |
| Behind the Scenes | Reversing | Very Easy | **Retired** | `UD2` anti-decompilation and four `strncmp` calls in GDB | [ES](challenges/Behind%20the%20Scenes/README.md) | [Ver](challenges/Behind%20the%20Scenes/README.en.md) |
| OnlyHacks | Web | Very Easy | **Retired** | IDOR at `/chat?rid=3`: the flag sits in another user's chat (the bot XSS is an alternative) | [ES](challenges/OnlyHacks/README.md) | [Ver](challenges/OnlyHacks/README.en.md) |
| Perfect Synchronization | Crypto | Easy | **Retired** | Per-character substitution (`char + 15`): frequency analysis, not AES-ECB | [ES](challenges/Perfect%20Synchronization/README.md) | [Ver](challenges/Perfect%20Synchronization/README.en.md) |
| xorxorxor | Crypto | Easy | **Retired** | Repeating-key XOR with a known prefix | [ES](challenges/xorxorxor/README.md) | [Ver](challenges/xorxorxor/README.en.md) |
| Baby Time Capsule | Crypto | Very Easy | **Retired** | RSA with small moduli: factor and decrypt | [ES](challenges/Baby%20Time%20Capsule/README.md) | [Ver](challenges/Baby%20Time%20Capsule/README.en.md) |
| Gunship | Web | Easy | **Retired** | Prototype pollution in `flat@5.0.0` + AST injection in the template engine | [ES](challenges/Gunship/README.md) | [Ver](challenges/Gunship/README.en.md) |
| baby interdimensional internet | Web | Easy | **Retired** | Python 2 `exec()` over `ingredient`/`measurements`, no filters | [ES](challenges/baby%20interdimensional%20internet/README.md) | [Ver](challenges/baby%20interdimensional%20internet/README.en.md) |
| Interdimensional Internet | Web | Medium | **Retired** | `[ ( _ .` WAF bypassed with `\x` and exfiltration via `flask.session` | [ES](challenges/Interdimensional%20Internet/README.md) | [Ver](challenges/Interdimensional%20Internet/README.en.md) |
| Fake Boost | Forensics | Easy | **Retired** | Reversed base64 PowerShell and AES exfiltration in a `POST` | [ES](challenges/Fake%20Boost/README.md) | [Ver](challenges/Fake%20Boost/README.en.md) |
| Impossible Password | Reversing | Easy | **Retired** | Second `strcmp` against `rand()`: equalise `$rdi`/`$rsi` in gdb | [ES](challenges/Impossible%20Password/README.md) | [Ver](challenges/Impossible%20Password/README.en.md) |
| Reg | Pwn | Easy | **Retired** | `gets()` in `run()`: `0x38` offset and ret2win into `winner()` with no PIE | [ES](challenges/Reg/README.md) | [Ver](challenges/Reg/README.en.md) |
| Survival of the Fittest | Blockchain | Very Easy | **Retired** | `strongAttack(20)` and `loot()` with no state check | [ES](challenges/Survival%20of%20the%20Fittest/README.md) | [Ver](challenges/Survival%20of%20the%20Fittest/README.en.md) |
| APKrypt | Mobile | Easy | **Retired** | AES key and blob inside the APK, ECB mode | [ES](challenges/APKrypt/README.md) | [Ver](challenges/APKrypt/README.en.md) |
| Photon Lockdown | Hardware | Very Easy | **Retired** | SquashFS with the factory password in `config_default.xml` | [ES](challenges/Photon%20Lockdown/README.md) | [Ver](challenges/Photon%20Lockdown/README.en.md) |
| Prometheon | AI/ML | Medium | **Retired** | Prompt injection across five chained levels | [ES](challenges/Prometheon/README.md) | [Ver](challenges/Prometheon/README.en.md) |
| Forks and Knives | Pwn | Medium | **Retired** | Off-by-one, format string, `fork()` canary and `dup2` ROP | [ES](challenges/Forks%20and%20Knives/README.md) | [Ver](challenges/Forks%20and%20Knives/README.en.md) |
| Evaluative | Coding | Very Easy | **Retired** | Degree-8 polynomial from nine coefficients: Horner with no powers | [ES](challenges/Evaluative/README.md) | [Ver](challenges/Evaluative/README.en.md) |
| Oddly Even | Coding | Very Easy | **Retired** | Parity with `% 2`; mind negatives in C | [ES](challenges/Oddly%20Even/README.md) | [Ver](challenges/Oddly%20Even/README.en.md) |
| Threat Index | Coding | Very Easy | **Retired** | 18 keywords weighted 1-18; `count` per term | [ES](challenges/Threat%20Index/README.md) | [Ver](challenges/Threat%20Index/README.en.md) |
| Watch Tower | ICS | Very Easy | **Retired** | Modbus/TCP PCAP: the flag lives in the function 16 `reference numbers` | [ES](challenges/Watch%20Tower/README.md) | [Ver](challenges/Watch%20Tower/README.en.md) |
| Intrusion | ICS | Easy | **Retired** | Holding registers with `unit id` 52, read with `umodbus`/`pymodbus` | [ES](challenges/Intrusion/README.md) | [Ver](challenges/Intrusion/README.en.md) |
| Factory | ICS | Easy | **Retired** | Ladder logic: manual mode and `Write Single Coil` to drain the tank | [ES](challenges/Factory/README.md) | [Ver](challenges/Factory/README.en.md) |
| Shush Protocol | ICS | Very Easy | **Retired** | Proprietary Modbus function 102: user and password in clear text in the TCP stream | [ES](challenges/Shush%20Protocol/README.md) | [Ver](challenges/Shush%20Protocol/README.en.md) |
| Sneak peek | ICS | Easy | **Retired** | Function `0x64`: overwrite the password MD5 in the memory block | [ES](challenges/Sneak%20peek/README.md) | [Ver](challenges/Sneak%20peek/README.en.md) |
| FlagCasino | Reversing | Very Easy | **Retired** | `srand` per character against a `check` array: brute force over the 95 printable seeds | [ES](challenges/FlagCasino/README.md) | [Ver](challenges/FlagCasino/README.en.md) |
| Simple Encryptor | Reversing | Very Easy | **Retired** | Time seed in the first 4 bytes; XOR with `rand()` and a left rotation | [ES](challenges/Simple%20Encryptor/README.md) | [Ver](challenges/Simple%20Encryptor/README.en.md) |
| Shattered Tablet | Reversing | Very Easy | **Retired** | 40 per-index comparisons in Ghidra: retype the buffer as `char[64]` | [ES](challenges/Shattered%20Tablet/README.md) | [Ver](challenges/Shattered%20Tablet/README.en.md) |
| Tear or Dear | Reversing | Medium | **Retired** | .NET WinForms with 32-bit dnSpy: breakpoint on the credential comparison | [ES](challenges/Tear%20or%20Dear/README.md) | [Ver](challenges/Tear%20or%20Dear/README.en.md) |
| Snakecode | Reversing | Easy | **Retired** | Python 2.7 `.pyc` with `marshal` + zlib; the Snake apple spells the flag | [ES](challenges/Snakecode/README.md) | [Ver](challenges/Snakecode/README.en.md) |
| Locked Away | Misc | Easy | **Retired** | PyJail: `blacklist.clear()` dodges the brackets, then `open_chest()` | [ES](challenges/Locked%20Away/README.md) | [Ver](challenges/Locked%20Away/README.en.md) |
| Hidden Path | Misc | Easy | **Retired** | `U+3164` (HANGUL FILLER) variable in the command array: `choice=6` runs the injected command | [ES](challenges/Hidden%20Path/README.md) | [Ver](challenges/Hidden%20Path/README.en.md) |
| Aptitude Test | Misc | Very Easy | **Retired** | Quiz over `nc`: ten answers, then the role and the flag | [ES](challenges/Aptitude%20Test/README.md) | [Ver](challenges/Aptitude%20Test/README.en.md) |
| Chrono Mind | Misc | Easy | **Retired** | `../config.py` path traversal as model context plus autocompletion RCE | [ES](challenges/Chrono%20Mind/README.md) | [Ver](challenges/Chrono%20Mind/README.en.md) |
| Super-Duper Pwn | Misc | Easy | **Retired** | Discord bot, `/checkout` template and `vm2` bypass via `Symbol.species` | [ES](challenges/Super-Duper%20Pwn/README.md) | [Ver](challenges/Super-Duper%20Pwn/README.en.md) |

- Achievement: https://labs.hackthebox.com/achievement/challenge/4187928/1926
- Category index and conventions: [challenges/README.en.md](challenges/README.en.md) · [ES](challenges/README.md)

---

## 🕵️ Sherlocks

Defensive investigation scenarios: nothing is attacked, you answer questions about an incident from evidence.

| Sherlock | Domain | Difficulty | Evidence | ES | EN |
|---|---|---|---|---|---|
| Phantom Check | DFIR | Very Easy | Two PowerShell EVTX logs: WMI and anti-VM | [ES](sherlocks/phantom-check/README.md) | [Ver](sherlocks/phantom-check/README.en.md) |
| TickTock | DFIR / Windows | Medium | MFT, TeamViewer, PowerShell and Defender | [ES](sherlocks/ticktock/README.md) | [Ver](sherlocks/ticktock/README.en.md) |
| CrownJewel-2 | DFIR / Active Directory | Medium | DC logs with pass-the-hash and `C$` access | [ES](sherlocks/crownjewel-2/README.md) | [Ver](sherlocks/crownjewel-2/README.en.md) |
| Campfire-2 | DFIR / Active Directory | Easy | 4768 without pre-authentication (AS-REP) and later use | [ES](sherlocks/campfire-2/README.md) | [Ver](sherlocks/campfire-2/README.en.md) |
| Safecracker | DFIR / Malware | Medium | Ransomware in a ZIP for Autopsy: accounts, encryption and deletion via `NtSetInformationFile` | [ES](sherlocks/safecracker/README.md) | [Ver](sherlocks/safecracker/README.en.md) |
| JenkreadD | DFIR / Web | Easy | Jenkins CVE-2024-23897: `POST /cli` with `@path` | [ES](sherlocks/jenkreadd/README.md) | [Ver](sherlocks/jenkreadd/README.en.md) |
| Subatomic | Malware / DFIR | Medium | Fake game installer: Electron `app.asar`, Discord token theft and `openAtLogin` | [ES](sherlocks/subatomic/README.md) | [Ver](sherlocks/subatomic/README.en.md) |
| Litter | SOC | Easy | PCAP + ZIP from a test host | [ES](sherlocks/litter/README.md) | [Ver](sherlocks/litter/README.en.md) |
| PhantomRing | Malware Analysis | Very Easy | Unstripped ELF in `/var/tmp`: `nm` yields the names and the C2 port is an immediate operand | [ES](sherlocks/phantomring/README.md) | [Ver](sherlocks/phantomring/README.en.md) |
| Opportunist | DFIR / Malware | Medium | Memory + triage from a corporate host | [ES](sherlocks/opportunist/README.md) | [Ver](sherlocks/opportunist/README.en.md) |
| dOOMs Day | DFIR | Easy | Web logs from a compromised PHP server | [ES](sherlocks/dooms-day/README.md) | [Ver](sherlocks/dooms-day/README.en.md) |
| Brutus | DFIR | Very Easy | Authentication logs | [ES](sherlocks/brutus/README.md) | [Ver](sherlocks/brutus/README.en.md) |
| MangoBleed | DFIR / Linux | Very Easy | UAC MongoDB triage: CVE-2025-14847 and `/var/lib/mongodb` exfiltration | [ES](sherlocks/mangobleed/README.md) | [Ver](sherlocks/mangobleed/README.en.md) |
| NeuroSync-D | DFIR / Web | Easy | Next.js CVE-2025-29927 → SSRF, LFI and Redis to RCE | [ES](sherlocks/neurosync-d/README.md) | [Ver](sherlocks/neurosync-d/README.en.md) |
| Campfire-1 | DFIR / Active Directory | Very Easy | Domain event logs | [ES](sherlocks/campfire-1/README.md) | [Ver](sherlocks/campfire-1/README.en.md) |
| CrownJewel-1 | DFIR / Active Directory | Medium | DC telemetry after a compromise | [ES](sherlocks/crownjewel-1/README.md) | [Ver](sherlocks/crownjewel-1/README.en.md) |
| Loggy | Malware / Go | Easy | `Loggy.exe`: Go keylogger with screenshots and FTP exfiltration | [ES](sherlocks/loggy/README.md) | [Ver](sherlocks/loggy/README.en.md) |
| Bumblebee | DFIR | Easy | phpBB SQLite database and `access.log` | [ES](sherlocks/bumblebee/README.md) | [Ver](sherlocks/bumblebee/README.en.md) |
| Heartbreaker-Denouement | Cloud / AWS | Medium | SSRF to the metadata service, role credentials and shared RDS snapshots | [ES](sherlocks/heartbreaker-denouement/README.md) | [Ver](sherlocks/heartbreaker-denouement/README.en.md) |
| Meerkat | SOC | Easy | PCAP and Suricata alerts | [ES](sherlocks/meerkat/README.md) | [Ver](sherlocks/meerkat/README.en.md) |
| Tracer | DFIR | Easy | PsExec nine times: `psexesvc.exe`, `.key`, named pipes and source host | [ES](sherlocks/tracer/README.md) | [Ver](sherlocks/tracer/README.en.md) |
| Noted | DFIR | Easy | Notepad++ artefacts | [ES](sherlocks/noted/README.md) | [Ver](sherlocks/noted/README.en.md) |
| Logjammer | Log Analysis | Easy | Five EVTX channels from one host | [ES](sherlocks/logjammer/README.md) | [Ver](sherlocks/logjammer/README.en.md) |
| Unit42 | DFIR | Very Easy | Sysmon y Dropbox en un host Windows | [ES](sherlocks/unit42/README.md) | [Ver](sherlocks/unit42/README.en.md) |
| BFT | DFIR | Very Easy | `$MFT` de un ZIP troyanizado | [ES](sherlocks/bft/README.md) | [Ver](sherlocks/bft/README.en.md) |
| Noxious | DFIR | Medium | PCAP with LLMNR/NBT-NS poisoning | [ES](sherlocks/noxious/README.md) | [Ver](sherlocks/noxious/README.en.md) |
| Reaper | DFIR | Very Easy | NTLM relay after a mistyped share: LLMNR, a 4624 whose IP and workstation disagree, 5140 | [ES](sherlocks/reaper/README.md) | [Ver](sherlocks/reaper/README.en.md) |
| Knock Knock | DFIR | Medium | PCAP de *password spray* y *port knocking* | [ES](sherlocks/knock-knock/README.md) | [Ver](sherlocks/knock-knock/README.en.md) |
| RogueOne | DFIR / Memoria | Easy | Fake `svchost.exe` in `Downloads` with C2 to 13.127.155.166:8888 and a `cmd.exe` child | [ES](sherlocks/rogueone/README.md) | [Ver](sherlocks/rogueone/README.en.md) |
| SSHole | DFIR / Unix | Very Easy | Alpine `sshd` bypass (crypt's `*`) on a jumpbox later used to scan `192.168.18.0/24` | [ES](sherlocks/sshole/README.md) | [Ver](sherlocks/sshole/README.en.md) |
| ShadowBait | DFIR / Windows | Easy | Steven's Office document → PowerShell → C2 `192.168.204.152:8899` → DPAPI and persistence | [ES](sherlocks/shadowbait/README.md) | [Ver](sherlocks/shadowbait/README.en.md) |
| Compromised | DFIR / Red | Easy | PCAP de una red corporativa | [ES](sherlocks/compromised/README.md) | [Ver](sherlocks/compromised/README.en.md) |
| Packet Puzzle | DFIR / Red | Medium | PCAP from a Japanese crypto company: CVE-2024-4577 in PHP 8.1.25 over POST, `cristo`, `nc64.exe`, GodPotato and `Win32Error:2` (`[CORREGIDO]` per cyb3rloud and FinalBreach) | [ES](sherlocks/packet-puzzle/README.md) | [Ver](sherlocks/packet-puzzle/README.en.md) |
| Jingle Bell | DFIR / Windows | Easy | Base de notificaciones de Windows de un puesto | [ES](sherlocks/jingle-bell/README.md) | [Ver](sherlocks/jingle-bell/README.en.md) |
| Ultimatum | DFIR / Web | Easy | CVE-2023-3460 in Ultimate Member: `secragon` admin, web shell and remote shell | [ES](sherlocks/ultimatum/README.md) | [Ver](sherlocks/ultimatum/README.en.md) |
| ProcNet | DFIR / Endpoint | Hard | Open-source C2: JA3, API Monitor (Vault) and Sysmon from employee and DC | [ES](sherlocks/procnet/README.md) | [Ver](sherlocks/procnet/README.en.md) |
| PCAP Analysis | DFIR / Red | Very Easy | P13's capture: cleartext chat on TCP/250 and a ~107 KB HTTP upload to another subnet | [ES](sherlocks/pcap-analysis/README.md) | [Ver](sherlocks/pcap-analysis/README.en.md) |
| Vantage | DFIR / Red | Very Easy | PCAP de servidor web y controlador de nube | [ES](sherlocks/vantage/README.md) | [Ver](sherlocks/vantage/README.en.md) |
| Lockpick | Malware / Ransomware | Easy | Muestra de ransomware y ficheros cifrados | [ES](sherlocks/lockpick/README.md) | [Ver](sherlocks/lockpick/README.en.md) |
| Lockpick 2.0 | Malware / Ransomware | Easy | Recurso compartido cifrado y muestra con nota | [ES](sherlocks/lockpick-2/README.md) | [Ver](sherlocks/lockpick-2/README.en.md) |
| Payload | Malware / Windows | Easy | `func_pointer.exe` (MinGW) decrypting its payload at runtime | [ES](sherlocks/payload/README.md) | [Ver](sherlocks/payload/README.en.md) |
| Takedown | Red / DFIR | Easy | PCAP with SMB2 → `.vbs` → PowerShell → C2, plus `NTLMSSP_AUTH` for pass-the-hash | [ES](sherlocks/takedown/README.md) | [Ver](sherlocks/takedown/README.en.md) |
| Interceptor | SOC / Red | Easy | PCAP de una infección SSLoad con C2 en RC4 | [ES](sherlocks/interceptor/README.md) | [Ver](sherlocks/interceptor/README.en.md) |
| Nubilum-1 | Cloud / AWS | Medium | CloudTrail, EC2 comprometida y copia de S3 | [ES](sherlocks/nubilum-1/README.md) | [Ver](sherlocks/nubilum-1/README.en.md) |
| Nubilum-2 | Cloud / AWS | Medium (sources: Easy) | S3 with anonymous read of an IAM key CSV and self-escalation via `PutUserPolicy` | [ES](sherlocks/nubilum-2/README.md) | [Ver](sherlocks/nubilum-2/README.en.md) |
| Hyperfiletable | DFIR / Windows | Easy | Sólo la MFT de un equipo con phishing | [ES](sherlocks/hyperfiletable/README.md) | [Ver](sherlocks/hyperfiletable/README.en.md) |
| WorkFromHome | DFIR / Windows | Medium | Phishing → RDP → `SeManageVolumePrivilege` → `PrintConfig.dll` and WMI persistence | [ES](sherlocks/workfromhome/README.md) | [Ver](sherlocks/workfromhome/README.en.md) |
| Lockpick 3.0 | Malware / Linux | Hard | XOR binary with the key passed as an argument, memory and systemd unit | [ES](sherlocks/lockpick-3/README.md) | [Ver](sherlocks/lockpick-3/README.en.md) |
| Jugglin | DFIR / WSL2 | Medium | `wsl.exe` API captures: exfiltration and `lsassy` dumping with no Windows log trace | [ES](sherlocks/jugglin/README.md) | [Ver](sherlocks/jugglin/README.en.md) |
| Heist | DFIR / Malware | Hard | Phishing → `Partnership.pdf.exe` → RedLine; PCAP, Prefetch and SRUM | [ES](sherlocks/heist/README.md) | [Ver](sherlocks/heist/README.en.md) |
| BOughT | DFIR / Malware | Hard | Memory + AD1: `StartUp` persistence, mutex, 59,049-domain DGA and DDoS | [ES](sherlocks/bought/README.md) | [Ver](sherlocks/bought/README.en.md) |
| Liberty | DFIR / Windows | Medium | Spray → RDP, Net-NTLMv2 theft via a `.url` and PowerShell Web Access | [ES](sherlocks/liberty/README.md) | [Ver](sherlocks/liberty/README.en.md) |
| Jinkies | DFIR / Windows | Medium | SMB with credentials, `bk_db.ibd` backup and reuse down to the local hash | [ES](sherlocks/jinkies/README.md) | [Ver](sherlocks/jinkies/README.en.md) |
| i-like-to | DFIR / MOVEit | Easy | KAPE triage of a MOVEit server: IIS logs, `$MFT`, EVTX, memory and SQL dump | [ES](sherlocks/i-like-to/README.md) | [Ver](sherlocks/i-like-to/README.en.md) |
| Pikaptcha | DFIR / Windows | Easy | PCAP and KAPE: fake captcha, clipboard and PowerShell | [ES](sherlocks/pikaptcha/README.md) | [Ver](sherlocks/pikaptcha/README.en.md) |
| Constellation | Threat Intelligence | Medium | PDF with insider instructions: metadata and timestamped URLs | [ES](sherlocks/constellation/README.md) | [Ver](sherlocks/constellation/README.en.md) |
| Heartbreaker-Continuum | DFIR / Malware | Easy | `.tiff.exe` with compiled PowerShell and SFTP exfiltration | [ES](sherlocks/heartbreaker-continuum/README.md) | [Ver](sherlocks/heartbreaker-continuum/README.en.md) |
| MisCloud | Cloud / GCP | Medium | `post-receive` hook, service account and bucket exfiltration | [ES](sherlocks/miscloud/README.md) | [Ver](sherlocks/miscloud/README.en.md) |
| Hunter | Threat Hunting | Insane | Endpoint triage and partial PCAP: 7045 service, Amcache, Prefetch, `Windows.edb` and FileZilla | [ES](sherlocks/hunter/README.md) | [Ver](sherlocks/hunter/README.en.md) |
| Trent | DFIR / Network | Medium | Router PCAP: CVE-2024-28353 and a reverse shell | [ES](sherlocks/trent/README.md) | [Ver](sherlocks/trent/README.en.md) |

- Index, methodology and pending notes: [sherlocks/README.en.md](sherlocks/README.en.md) · [ES](sherlocks/README.md)
- Note template: [templates/sherlock-template.en.md](templates/sherlock-template.en.md) · [ES](templates/sherlock-template.md)

---

## 🧠 Knowledge base

Reusable notes (each available in Spanish and English):

- [Spring Boot Actuator / heapdump](knowledge/web/actuator-heapdump.en.md) · [ES](knowledge/web/actuator-heapdump.md)
- [XXE](knowledge/web/xxe.en.md) · [ES](knowledge/web/xxe.md)
- [WordPress admin-bot XSS with a forged encrypted payload](knowledge/web/wp-admin-bot-xss.en.md) · [ES](knowledge/web/wp-admin-bot-xss.md)
- [ClickHouse cheatsheet](knowledge/clickhouse/cheatsheet.en.md) · [ES](knowledge/clickhouse/cheatsheet.md)
- [Credential capture via `/proc`](knowledge/linux/proc-credential-capture.en.md) · [ES](knowledge/linux/proc-credential-capture.md)
- [systemd timers and privesc](knowledge/privesc/systemd-timers.en.md) · [ES](knowledge/privesc/systemd-timers.md)
- [Craft CMS: CP utilities and environment secrets](knowledge/web/craft-cms-cp-utilities.en.md) · [ES](knowledge/web/craft-cms-cp-utilities.md)
- [MSSQL: decrypting credentials and abusing SeBackupPrivilege](knowledge/windows/mssql-credentials-sebackup.en.md) · [ES](knowledge/windows/mssql-credentials-sebackup.md)
- [XOR and encoding chains](knowledge/crypto/xor-and-encodings.en.md) · [ES](knowledge/crypto/xor-and-encodings.md)
- [RSA: small modulus and textbook RSA](knowledge/crypto/rsa-small-modulus.en.md) · [ES](knowledge/crypto/rsa-small-modulus.md)
- [Block and custom ciphers](knowledge/crypto/block-ciphers.en.md) · [ES](knowledge/crypto/block-ciphers.md)
- [SSTI: from template to execution](knowledge/web/ssti.en.md) · [ES](knowledge/web/ssti.md)
- [SQLi in the login: authentication bypass](knowledge/web/sqli-auth-bypass.en.md) · [ES](knowledge/web/sqli-auth-bypass.md)
- [SMB enumeration: null sessions, shares and credentials](knowledge/general/smb-enumeration.en.md) · [ES](knowledge/general/smb-enumeration.md)
- [Misconfigured S3: open buckets and webshells](knowledge/cloud/s3-misconfiguration.en.md) · [ES](knowledge/cloud/s3-misconfiguration.md)
- [Log4Shell: from a User-Agent to RCE](knowledge/web/log4shell.en.md) · [ES](knowledge/web/log4shell.md)
- [PHP deserialization](knowledge/web/php-deserialization.en.md) · [ES](knowledge/web/php-deserialization.md)
- [JWT and prototype pollution](knowledge/web/node-jwt-prototype.en.md) · [ES](knowledge/web/node-jwt-prototype.md)
- [PCAP triage](knowledge/forensics/pcap-triage.en.md) · [ES](knowledge/forensics/pcap-triage.md)
- [Windows artifacts: EVTX, MFT and Prefetch](knowledge/forensics/windows-artifacts.en.md) · [ES](knowledge/forensics/windows-artifacts.md)
- [Linux privesc: sudo, SUID, capabilities and cron](knowledge/privesc/linux-sudo-suid.en.md) · [ES](knowledge/privesc/linux-sudo-suid.md)
- [Kerberos: AS-REP, Kerberoast and GPP](knowledge/windows/kerberos-enum.en.md) · [ES](knowledge/windows/kerberos-enum.md)
- [Pivoting: SSH, chisel and Ligolo-ng](knowledge/general/pivoting.en.md) · [ES](knowledge/general/pivoting.md)
- [LFI: from file read to code execution](knowledge/web/lfi-to-rce.en.md) · [ES](knowledge/web/lfi-to-rce.md)
- [Windows privesc: SeImpersonate, services and LAPS](knowledge/windows/privesc-windows.en.md) · [ES](knowledge/windows/privesc-windows.md)
- [Exploiting a CVE: version, PoC and adaptation](knowledge/web/cve-workflow.en.md) · [ES](knowledge/web/cve-workflow.md)
- [AD CS: ESC13 (issuance policy linked to a group)](knowledge/windows/adcs-esc13.en.md) · [ES](knowledge/windows/adcs-esc13.md)
- [AD CS: ESC1 (the requester chooses the subject)](knowledge/windows/adcs-esc1.en.md) · [ES](knowledge/windows/adcs-esc1.md)
- [Shadow credentials, KrbRelay and KrbRelayUp](knowledge/windows/shadow-credentials-krbrelay.en.md) · [ES](knowledge/windows/shadow-credentials-krbrelay.md)
- [AD CS: ESC4 → ESC1](knowledge/windows/adcs-esc4-esc1.en.md) · [ES](knowledge/windows/adcs-esc4-esc1.md)
- [gMSA: read the managed password through the group](knowledge/windows/gmsa-read-key.en.md) · [ES](knowledge/windows/gmsa-read-key.md)
- [JEA: restricted endpoints and PSReadLine](knowledge/windows/jea.en.md) · [ES](knowledge/windows/jea.md)
- [RBCD and S4U2Proxy](knowledge/windows/rbcd-s4u2proxy.en.md) · [ES](knowledge/windows/rbcd-s4u2proxy.md)
- [MSSQL: from sysadmin to SYSTEM and DCSync](knowledge/windows/mssql-exec.en.md) · [ES](knowledge/windows/mssql-exec.md)
- [Kerberos and the clock: the 5-minute skew](knowledge/general/kerberos-clock.en.md) · [ES](knowledge/general/kerberos-clock.md)
- [Getting in: SSH, RDP, WinRM, SMB and BitLocker keys](knowledge/general/remote-access.en.md) · [ES](knowledge/general/remote-access.md)
- [Attack channel: Kali VM, VPN and preflight check](knowledge/general/lab-setup.en.md) · [ES](knowledge/general/lab-setup.md)
- [Stack overflow and ROP on x86-64](knowledge/pwn/rop-stack.en.md) · [ES](knowledge/pwn/rop-stack.md)
- [Phishing infrastructure: from email to domain](knowledge/osint/phishing-infrastructure.en.md) · [ES](knowledge/osint/phishing-infrastructure.md)
- [Steganography in images and audio](knowledge/stego/images-audio.en.md) · [ES](knowledge/stego/images-audio.md)
- [APK analysis: from `jadx` to Frida](knowledge/mobile/apk-analysis.en.md) · [ES](knowledge/mobile/apk-analysis.md)
- [Hardware: UART, firmware and extraction](knowledge/hardware/uart-firmware.en.md) · [ES](knowledge/hardware/uart-firmware.md)
- [Prototype pollution and AST injection](knowledge/web/prototype-pollution-ast.en.md) · [ES](knowledge/web/prototype-pollution-ast.md)
- [WSL2 in DFIR: host artifacts and API capture](knowledge/forensics/wsl2-dfir.en.md) · [ES](knowledge/forensics/wsl2-dfir.md)
- [AD ACL chains: from GenericAll to DCSync](knowledge/windows/ad-acl-chains.en.md) · [ES](knowledge/windows/ad-acl-chains.md)
- [RedLine Stealer: delivery chain, C2 and artifacts](knowledge/forensics/malware-redline.en.md) · [ES](knowledge/forensics/malware-redline.md)
- [ImageMagick CVE-2022-44268: arbitrary file read](knowledge/linux/imagemagick-file-read.en.md) · [ES](knowledge/linux/imagemagick-file-read.md)
- [AD Recycle Bin: deleted objects as a credential source](knowledge/windows/ad-recycle-bin.en.md) · [ES](knowledge/windows/ad-recycle-bin.md)
- [MOVEit CVE-2023-34362: exploitation and DFIR artifacts](knowledge/forensics/moveit-cve-2023-34362.en.md) · [ES](knowledge/forensics/moveit-cve-2023-34362.md)
- [`logrotate` race with a writable directory](knowledge/linux/logrotate-race.en.md) · [ES](knowledge/linux/logrotate-race.md)
- [Modbus/TCP in captures: registers, functions and extraction](knowledge/ics/modbus-pcap.en.md) · [ES](knowledge/ics/modbus-pcap.md)
- [Entra ID and Sentinel: sign-ins, audit and KQL](knowledge/cloud/entra-id-sentinel.en.md) · [ES](knowledge/cloud/entra-id-sentinel.md)
- [TeamViewer 7 and CVE-2019-18988: shared AES key](knowledge/windows/teamviewer-cve-2019-18988.en.md) · [ES](knowledge/windows/teamviewer-cve-2019-18988.md)
- [Prompt injection: getting what the model should not say](knowledge/ai/prompt-injection.en.md) · [ES](knowledge/ai/prompt-injection.md)
- [Smart contracts: state, payments and typical surface](knowledge/blockchain/smart-contracts.en.md) · [ES](knowledge/blockchain/smart-contracts.md)
- [PRNG, seeds and key schedules](knowledge/reversing/prng-keyschedule.en.md) · [ES](knowledge/reversing/prng-keyschedule.md)
- [PyJail: blacklists and escapes](knowledge/misc/pyjail-bypass.en.md) · [ES](knowledge/misc/pyjail-bypass.md)
- [Threat hunting: hypotheses, pivots and evidence](knowledge/threat-hunting/threat-hunting.en.md) · [ES](knowledge/threat-hunting/threat-hunting.md)
- [Invisible characters and Unicode backdoors](knowledge/misc/unicode-invisible.en.md) · [ES](knowledge/misc/unicode-invisible.md)
- [.NET: triage, dnSpy and debugging](knowledge/reversing/dotnet-dnspy.en.md) · [ES](knowledge/reversing/dotnet-dnspy.md)
- [Context injection and autocompletion in models](knowledge/ai/lm-context-injection.en.md) · [ES](knowledge/ai/lm-context-injection.md)
- [Format strings: reading and writing with printf](knowledge/pwn/format-strings.en.md) · [ES](knowledge/pwn/format-strings.md)
- [Partial overwrite of return addresses](knowledge/pwn/partial-overwrite.en.md) · [ES](knowledge/pwn/partial-overwrite.md)
- [C strings and null bytes: silent truncation](knowledge/pwn/null-byte-truncation.en.md) · [ES](knowledge/pwn/null-byte-truncation.md)
- [Canary, PIE and ROP: from leak to shell](knowledge/pwn/canary-pie-rop.en.md) · [ES](knowledge/pwn/canary-pie-rop.md)
- [DirtyPipe (CVE-2022-0847): writing into the page cache](knowledge/linux/kernel-dirty-pipe.en.md) · [ES](knowledge/linux/kernel-dirty-pipe.md)

---

## 🧭 Methodology

1. **Recon:** `nmap`, vhosts, technologies.
2. **Enumeration:** web, SMB, FTP, databases, APIs.
3. **Foothold:** credentials, vulnerabilities, XXE, IDOR, etc.
4. **Lateral movement:** credential reuse, pivoting.
5. **Privilege escalation:** SUID, capabilities, systemd, backups.
6. **Evidence and cleanup.**
7. **Mitigation and detection.**

---

## 🛠️ Skills

| Area | Level | Evidence |
|---|---|---|
| Web enumeration | 🟢🟢🟢⚪⚪ | Cap, Stream |
| Linux privesc | 🟢🟢🟢⚪⚪ | Cap, Stream |
| Windows / AD | 🟢⚪⚪⚪⚪ | Dancing |
| Cloud | ⚪⚪⚪⚪⚪ | — |

---

## ✅ Quality

The `.githooks/pre-commit` hook runs `private/scripts/verify.py` and `private/scripts/audit-indices.py` before every commit. It blocks the commit on broken links, missing or orphan index rows, bad language headers or malformed root tables.

To enable it in a fresh clone, run the installer:

```bash
.githooks/install.sh
```

It checks Python 3.8+, the hook and both scripts, and only then sets `core.hooksPath`. You can also do it by hand with `git config core.hooksPath .githooks`.

- Requires **Python 3.8 or later**.
- Both scripts live in `private/scripts/`, which is git-ignored: copy them into the clone or the hook will block with `falta ...`.
- Manual run: `.githooks/pre-commit` (or each script separately).
- Hook test: `.githooks/test.sh`.
- Before publishing: `.githooks/pre-publish.sh` (the `pre-push` hook runs it).
- Disable it: `git config --unset core.hooksPath`.
- Skip the hooks: `git commit --no-verify` or `git push --no-verify`. Use it only for an emergency and run `.githooks/pre-publish.sh` afterwards; it is not a way around broken links or mismatched indexes.

The configuration is local and is not versioned.

---

## 📁 Structure

```text
htb-writeups/
├── README.md               # Index (ES)
├── README.en.md            # Index (EN)
├── .githooks/
│   ├── pre-commit          # quality hook (links and indexes)
│   ├── pre-push            # runs the task before publishing
│   ├── install.sh          # checks requirements and enables the hook
│   ├── test.sh             # tests installer and hook blocking
│   └── pre-publish.sh      # tests + links + indexes
├── templates/
│   ├── machine-template.md      # machine template ES
│   ├── machine-template.en.md   # machine template EN
│   ├── challenge-template.md    # challenge template ES
│   ├── challenge-template.en.md # challenge template EN
│   ├── sherlock-template.md     # Sherlock template ES
│   └── sherlock-template.en.md  # Sherlock template EN
├── challenges/
│   ├── README.md        # challenge index ES/EN
│   ├── README.en.md
│   └── Dark Embargo/    # README.md + README.en.md + exploit.py
├── machines/
│   ├── catalog.md       # retired machine catalogue ES/EN
│   ├── catalog.en.md
│   ├── starting-point/
│   │   ├── README.md    # Track index ES/EN
│   │   ├── meow/        # README.md + README.en.md
│   │   └── ...          # 25 notes: Tier 0, 1 and 2
│   ├── linux/
│   │   ├── cap/
│   │   ├── makesense/
│   │   ├── admirer/
│   │   ├── airtouch/
│   │   ├── armageddon/
│   │   ├── bank/
│   │   ├── cobblestone/
│   │   ├── code/
│   │   ├── helix/
│   │   ├── interpreter/
│   │   ├── kobold/
│   │   ├── variatype/
│   │   ├── bashed/
│   │   ├── beep/
│   │   ├── blocky/
│   │   ├── blunder/
│   │   ├── delivery/
│   │   ├── facts/
│   │   ├── cronos/
│   │   ├── sink/
│   │   ├── sorcery/
│   │   └── friendzone/
│   ├── windows/
│   │   ├── active/
│   │   ├── arctic/
│   │   ├── bastion/
│   │   ├── blue/
│   │   ├── eighteen/
│   │   ├── bounty/
│   │   ├── forest/
│   │   └── pingpong/
│   └── active/          # active machines: gitignored, not published
│       ├── dutybound/
│       ├── stream/
│       ├── layover/
│       ├── connected/
│       └── unclaimed/
├── sherlocks/
│   ├── README.md        # Sherlock index ES/EN
│   ├── README.en.md
│   └── litter/          # README.md + README.en.md
├── knowledge/
│   ├── web/
│   ├── windows/
│   ├── general/
│   ├── crypto/
│   ├── forensics/
│   ├── privesc/
│   ├── linux/
│   ├── cloud/
│   ├── pwn/
│   ├── osint/
│   ├── stego/
│   ├── mobile/
│   ├── hardware/
│   ├── ics/
│   ├── ai/
│   ├── blockchain/
│   ├── misc/
│   ├── reversing/
│   ├── threat-hunting/
│   └── clickhouse/
└── private/             # git-ignored: real credentials and flags
```

---

## ⚠️ Legal notice

All the content was produced in authorized **Hack The Box** labs. No flags, credentials or private keys are published. This material is for educational purposes only.

Writeups for **active** machines remain private drafts and are only published once HTB marks them as **Retired**, in compliance with the platform policy.

---

## 📄 License

Content under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Code under MIT.
