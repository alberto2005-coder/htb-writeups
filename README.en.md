# 🎯 HTB Writeups — alberto2005coder

[🇪🇸 Español](README.md) | **English**

Personal repository of **Hack The Box** writeups, notes and methodology.

> **Status:** work in progress. **Active** machines are not published until HTB retires them.
>
> **Numbers:** 94 machines, 50 Sherlocks, 50 challenges and 36 knowledge topics, each in ES/EN.

---

## 👤 Profile

- **HTB:** [alberto2005coder](https://app.hackthebox.com/users/4187928)
- **Focus:** web pentesting, Linux, Active Directory and cloud.
- **Goal:** document the full process (recon → foothold → privilege escalation → mitigation), not just the final command.

---

## 🗂️ Machines

| Machine | OS | Difficulty | Category | State | Key techniques | ES | EN |
|---|---|---|---|---|---|---|---|
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
| Cap | Linux | Easy | Machines | Retired | IDOR, pcap analysis, `cap_setuid` | [ES](machines/linux/cap/README.md) | [Ver](machines/linux/cap/README.en.md) |
| MakeSense | Linux | Medium | Season 11 | Retired | Admin-bot XSS, forged AES-GCM, malicious plugin, OCR as root | [ES](machines/linux/makesense/README.md) | [Ver](machines/linux/makesense/README.en.md) |
| DutyBound | Linux | Medium | Season 12 | **Active** | BCBP, PostgreSQL SQLi, `COPY TO PROGRAM`, X11/XTEST, path unit with `eval` | [ES](machines/active/dutybound/README.md) | [Draft](machines/active/dutybound/README.en.md) |
| Stream | Linux | Medium | Season 12 | **Active** | Heapdump, XXE, ClickHouse, Kopia, root timer | [ES](machines/active/stream/README.md) | [Draft](machines/active/stream/README.en.md) |
| Layover | Linux | Medium | Season 12 | **Active** | Cleartext WiFi credentials, Craft CP utilities (DB backup + phpinfo), Yii decryption, CUPS 2.4.16 CVE-2026-34990 | [ES](machines/active/layover/README.md) | [Draft](machines/active/layover/README.en.md) |
| Connected | Linux | Easy | Season 11 | **Active** | FreePBX 16: stacked SQLi CVE-2025-57819 + path traversal CVE-2025-61678 to webshell, then incron with a root-sourced `init.conf` | [ES](machines/active/connected/README.md) | [Draft](machines/active/connected/README.en.md) |
| Unclaimed | Windows | Medium | Season 12 | **Active** | Chatbot over SQL: `IMPERSONATE` to sysadmin, `xp_cmdshell`, DPAPI decryption of a credential, and `SeBackupPrivilege` with `robocopy /B` | [ES](machines/active/unclaimed/README.md) | [Draft](machines/active/unclaimed/README.en.md) |
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
| Dark Embargo | Web / Pwn | Medium | **Retired** | PHP 8.4.26: OOM in `session.upload_progress` → use-after-free (CVE-2026-109618/619), ASLR leak via `Set-Cookie`, `pDestructor` → `system()` | [ES](challenges/Dark%20Embargo/README.md) | [Ver](challenges/Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | **Retired** | MD5 against the clock: session handling, regex, automation | [ES](challenges/Emdee%20five%20for%20life/README.md) | [Ver](challenges/Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | **Retired** | LDAP injection in login and search (`*` wildcard) | [ES](challenges/Phonebook/README.md) | [Ver](challenges/Phonebook/README.en.md) |
| Under Construction | Web | Easy | **Retired** | JWT algorithm confusion: sign HS256 with the public key | [ES](challenges/Under%20Construction/README.md) | [Ver](challenges/Under%20Construction/README.en.md) |
| Gunship | Web | Easy | **Retired** | Prototype pollution in `flat@5.0.0` and AST injection in the template engine (Handlebars and Pug variants) | [ES](challenges/Gunship/README.md) | [Ver](challenges/Gunship/README.en.md) |
| baby interdimensional internet | Web | Easy | **Retired** | Python 2 `exec()` over `ingredient`/`measurements`, no filters or limits | [ES](challenges/baby%20interdimensional%20internet/README.md) | [Ver](challenges/baby%20interdimensional%20internet/README.en.md) |
| Interdimensional Internet | Web | Medium | **Retired** | `[ ( _ .` WAF bypassed with `\x5b\x28\x5f\x2e` and exfiltration via `flask.session` | [ES](challenges/Interdimensional%20Internet/README.md) | [Ver](challenges/Interdimensional%20Internet/README.en.md) |
| Fake Boost | Forensics | Easy | **Retired** | Reversed base64 PowerShell, AES-CBC and HTTP exfiltration in a `POST` | [ES](challenges/Fake%20Boost/README.md) | [Ver](challenges/Fake%20Boost/README.en.md) |
| Impossible Password | Reversing | Easy | **Retired** | Second `strcmp` against `rand()`: equalise `$rdi`/`$rsi` in gdb | [ES](challenges/Impossible%20Password/README.md) | [Ver](challenges/Impossible%20Password/README.en.md) |

- Achievement: https://labs.hackthebox.com/achievement/challenge/4187928/1926
- Category index and conventions: [challenges/README.en.md](challenges/README.en.md) · [ES](challenges/README.md)

---

## 🕵️ Sherlocks

Defensive investigation scenarios: nothing is attacked, you answer questions about an incident from evidence.

| Sherlock | Domain | Difficulty | Evidence | ES | EN |
|---|---|---|---|---|---|
| Litter | SOC | Easy | PCAP with DNS tunnelling (dnscat2) and host ZIP | [ES](sherlocks/litter/README.md) | [Ver](sherlocks/litter/README.en.md) |
| Jugglin | DFIR / WSL2 | Medium | `wsl.exe` API captures: exfiltration and `lsassy` with no Windows log trace | [ES](sherlocks/jugglin/README.md) | [Ver](sherlocks/jugglin/README.en.md) |
| Heist | DFIR / Malware | Hard | `Partnership.pdf.exe` → RedLine, PCAP, Prefetch and SRUM | [ES](sherlocks/heist/README.md) | [Ver](sherlocks/heist/README.en.md) |
| BOughT | DFIR / Malware | Hard | Memory + AD1, `StartUp` persistence, mutex, 59,049-domain DGA and DDoS | [ES](sherlocks/bought/README.md) | [Ver](sherlocks/bought/README.en.md) |
| Liberty | DFIR / Windows | Medium | Spray → RDP, Net-NTLMv2 theft via a `.url` and PowerShell Web Access | [ES](sherlocks/liberty/README.md) | [Ver](sherlocks/liberty/README.en.md) |
| Jinkies | DFIR / Windows | Medium | SMB with credentials, `bk_db.ibd` backup and reuse down to the local hash | [ES](sherlocks/jinkies/README.md) | [Ver](sherlocks/jinkies/README.en.md) |

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

## 📁 Structure

```text
htb-writeups/
├── README.md               # Index (ES)
├── README.en.md            # Index (EN)
├── templates/
│   ├── machine-template.md      # machine template ES
│   ├── machine-template.en.md   # machine template EN
│   ├── challenge-template.md    # challenge template ES
│   └── challenge-template.en.md # challenge template EN
├── challenges/
│   ├── README.md        # challenge index ES/EN
│   ├── README.en.md
│   └── Dark Embargo/    # README.md + README.en.md + exploit.py
├── machines/
│   ├── catalog.md       # retired machine catalogue ES/EN
│   ├── catalog.en.md
│   ├── starting-point/
│   │   ├── README.md    # Índice del itinerario ES/EN
│   │   ├── meow/        # README.md + README.en.md
│   │   ├── fawn/
│   │   ├── dancing/
│   │   ├── explosion/
│   │   ├── mongod/
│   │   ├── preignition/
│   │   ├── sequel/
│   │   ├── synced/
│   │   └── redeemer/
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
│   ├── clickhouse/
│   ├── crypto/
│   ├── forensics/
│   ├── linux/
│   ├── general/
│   ├── privesc/
│   └── windows/
└── private/             # git-ignored: real credentials and flags
```

---

## ⚠️ Legal notice

All the content was produced in authorized **Hack The Box** labs. No flags, credentials or private keys are published. This material is for educational purposes only.

Writeups for **active** machines remain private drafts and are only published once HTB marks them as **Retired**, in compliance with the platform policy.

---

## 📄 License

Content under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Code under MIT.
