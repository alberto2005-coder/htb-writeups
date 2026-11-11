# Retired machine catalogue

**English** | [🇪🇸 Español](catalog.md)

Reference notes for machines used to study techniques. The main table covers **retired** boxes; at the end there is a section with the 25 **Starting Point** machines, which are still available on the platform. Rows marked `ref.` were not played on this profile: they are study material, not an achievement, and carry no flags or credentials. Machines that were played live live in `machines/linux/`, `machines/windows/` or `machines/starting-point/` and appear in the main index.

## Written

| Machine | OS | Difficulty | Main technique | ES | EN |
|---|---|---|---|---|---|
| Sizzle | Windows | Insane | SCF/Responder, ADCS, Kerberoasting and DCSync | [ES](../machines/windows/sizzle/README.md) | [Ver](../machines/windows/sizzle/README.en.md) |
| Reel | Windows | Hard | RTF CVE-2017-0199, WriteOwner/WriteDacl ACLs and backup script | [ES](../machines/windows/reel/README.md) | [Ver](../machines/windows/reel/README.en.md) |
| Absolute | Windows | Insane | AS-REP, shadow credentials, KrbRelay and DCSync | [ES](../machines/windows/absolute/README.md) | [Ver](../machines/windows/absolute/README.en.md) |
| Multimaster | Windows | Insane | SQLi, CEF debug, GenericWrite/AS-REP and Server Operators | [ES](../machines/windows/multimaster/README.md) | [Ver](../machines/windows/multimaster/README.en.md) |
| Authority | Windows | Medium | Anonymous SMB, Ansible Vault, PWM, ESC1 (`CorpVPN`) and PassTheCert | [ES](../machines/windows/authority/README.md) | [Ver](../machines/windows/authority/README.en.md) |
| Sauna | Windows | Easy | AS-REP roasting, autologon credentials and DCSync | [ES](../machines/windows/sauna/README.md) | [Ver](../machines/windows/sauna/README.en.md) |
| Netmon | Windows | Easy | Anonymous FTP, PRTG and CVE-2018-9276 | [ES](../machines/windows/netmon/README.md) | [Ver](../machines/windows/netmon/README.en.md) |
| Servmon | Windows | Easy | NVMS path traversal, NSClient++ and SSH tunnel | [ES](../machines/windows/servmon/README.md) | [Ver](../machines/windows/servmon/README.en.md) |
| Resolute | Windows | Medium | Anonymous LDAP, password reuse and `DnsAdmins` | [ES](../machines/windows/resolute/README.md) | [Ver](../machines/windows/resolute/README.en.md) |
| Bastard | Windows | Medium | Drupalgeddon2 and JuicyPotato | [ES](../machines/windows/bastard/README.md) | [Ver](../machines/windows/bastard/README.en.md) |
| Cap | Linux | Easy | IDOR, pcap, `cap_setuid` | [ES](../machines/linux/cap/README.md) | [Ver](../machines/linux/cap/README.en.md) |
| Active | Windows | Easy | GPP in SYSVOL, Kerberoasting `Administrator` | [ES](../machines/windows/active/README.md) | [Ver](../machines/windows/active/README.en.md) |
| Armageddon | Linux | Easy | Drupal 7.56, Drupalgeddon2, snap hook | [ES](../machines/linux/armageddon/README.md) | [Ver](../machines/linux/armageddon/README.en.md) |
| Bashed | Linux | Easy | `phpbash` web shell, `sudo -u`, root cron | [ES](../machines/linux/bashed/README.md) | [Ver](../machines/linux/bashed/README.en.md) |
| Bastion | Windows | Easy | SMB backup with VHDX, SAM/SYSTEM, mRemoteNG | [ES](../machines/windows/bastion/README.md) | [Ver](../machines/windows/bastion/README.en.md) |
| Beep | Linux | Easy | Elastix LFI, CVE-2012-4869, interactive `nmap` | [ES](../machines/linux/beep/README.md) | [Ver](../machines/linux/beep/README.en.md) |
| Blocky | Linux | Easy | credentials in a JAR, reuse, `sudo ALL` | [ES](../machines/linux/blocky/README.md) | [Ver](../machines/linux/blocky/README.en.md) |
| Blunder | Linux | Easy | Bludit, brute-force bypass, `sudo -u#-1` | [ES](../machines/linux/blunder/README.md) | [Ver](../machines/linux/blunder/README.en.md) |
| Bounty | Windows | Easy | `web.config` on IIS, `SeImpersonate`, JuicyPotato | [ES](../machines/windows/bounty/README.md) | [Ver](../machines/windows/bounty/README.en.md) |
| Delivery | Linux | Easy | osTicket + Mattermost, bcrypt with rules | [ES](../machines/linux/delivery/README.md) | [Ver](../machines/linux/delivery/README.en.md) |
| Facts | Linux | Easy | Camaleon CMS, MinIO, SSH key, `facter` | [ES](../machines/linux/facts/README.md) | [Ver](../machines/linux/facts/README.en.md) |
| Forest | Windows | Easy | AS-REP, `Account Operators` to Exchange, DCSync | [ES](../machines/windows/forest/README.md) | [Ver](../machines/windows/forest/README.en.md) |
| FriendZone | Linux | Easy | AXFR, LFI + SMB, `os.py` hijack | [ES](../machines/linux/friendzone/README.md) | [Ver](../machines/linux/friendzone/README.en.md) |
| Admirer | Linux | Easy | Adminer 4.6.2, LFI via rogue MySQL, `PYTHONPATH` | [ES](../machines/linux/admirer/README.md) | [Ver](../machines/linux/admirer/README.en.md) |
| Arctic | Windows | Easy | ColdFusion 8 + FCKeditor, JuicyPotato | [ES](../machines/windows/arctic/README.md) | [Ver](../machines/windows/arctic/README.en.md) |
| Bank | Linux | Easy | AXFR, `302` to `200`, `.htb` upload, SUID | [ES](../machines/linux/bank/README.md) | [Ver](../machines/linux/bank/README.en.md) |
| Blue | Windows | Easy | MS17-010 EternalBlue | [ES](../machines/windows/blue/README.md) | [Ver](../machines/windows/blue/README.en.md) |
| Cronos | Linux | Medium | AXFR, SQLi, command injection, `artisan` cron | [ES](../machines/linux/cronos/README.md) | [Ver](../machines/linux/cronos/README.en.md) |
| PingPong | Windows | Insane | Dual AD forest, ESC13, pivot, gMSA, JEA, RBCD and ESC4→ESC1 | [ES](../machines/windows/pingpong/README.md) | [Ver](../machines/windows/pingpong/README.en.md) |
| AirTouch | Linux | Medium | WPA2, PEAP Evil Twin, VPN pivot | [ES](../machines/linux/airtouch/README.md) | [Ver](../machines/linux/airtouch/README.en.md) |
| Eighteen | Windows | Hard | `IMPERSONATE`, Werkzeug, CVE-2025-53779 | [ES](../machines/windows/eighteen/README.md) | [Ver](../machines/windows/eighteen/README.en.md) |
| Sink | Linux | Insane | Smuggling, Gitea, AWS KMS | [ES](../machines/linux/sink/README.md) | [Ver](../machines/linux/sink/README.en.md) |
| Sorcery | Linux | Insane | Cypher, WebAuthn, Kafka, FreeIPA | [ES](../machines/linux/sorcery/README.md) | [Ver](../machines/linux/sorcery/README.en.md) |
| Cobblestone | Linux | Insane | Second-order SQLi, Twig SSTI, Cobbler | [ES](../machines/linux/cobblestone/README.md) | [Ver](../machines/linux/cobblestone/README.en.md) |
| Code | Linux | Easy | Python sandbox escape, bcrypt, `backy.sh` | [ES](../machines/linux/code/README.md) | [Ver](../machines/linux/code/README.en.md) |
| Kobold | Linux | Easy | MCPJam CVE-2026-23744, PrivateBin, Docker | [ES](../machines/linux/kobold/README.md) | [Ver](../machines/linux/kobold/README.en.md) |
| Helix | Linux | Medium | NiFi + H2 `CREATE ALIAS`, OPC UA | [ES](../machines/linux/helix/README.md) | [Ver](../machines/linux/helix/README.en.md) |
| Interpreter | Linux | Medium | Mirth CVE-2023-43208, PBKDF2, `eval()` | [ES](../machines/linux/interpreter/README.md) | [Ver](../machines/linux/interpreter/README.en.md) |
| VariaType | Linux | Medium | fontTools, FontForge, setuptools | [ES](../machines/linux/variatype/README.md) | [Ver](../machines/linux/variatype/README.en.md) |
| Pirate | Windows | Hard | Pre-Windows 2000, gMSA, RBCD, S4U2Proxy | [ES](../machines/windows/pirate/README.md) | [Ver](../machines/windows/pirate/README.en.md) |
| MonitorsFour | Windows | Easy | IDOR en la API, MD5 crackeado, CVE-2025-24367 en Cacti, escape por la API de Docker | [ES](../machines/windows/monitorsfour/README.md) | [Ver](../machines/windows/monitorsfour/README.en.md) |
| Pterodactyl | Linux | Medium | CVE-2025-49132 en `/locales`, PEAR `pearcmd`, cadena CVE-2025-6018/6019 | [ES](../machines/linux/pterodactyl/README.md) | [Ver](../machines/linux/pterodactyl/README.en.md) |
| Buff | Windows | Easy | Subida sin autenticacion, CloudMe 1.11.2 | [ES](../machines/windows/buff/README.md) | [Ver](../machines/windows/buff/README.en.md) |
| Blackfield | Windows | Hard | AS-REP, volcado de lsass, SeBackupPrivilege, NTDS | [ES](../machines/windows/blackfield/README.md) | [Ver](../machines/windows/blackfield/README.en.md) |
| Nibbles | Linux | Easy | Nibbleblog 4.0.3, subida CVE-2015-6967, sudo | [ES](../machines/linux/nibbles/README.md) | [Ver](../machines/linux/nibbles/README.en.md) |
| Doctor | Linux | Easy | SSTI con Jinja2 en un vhost, Splunk 8.0.x | [ES](../machines/linux/doctor/README.md) | [Ver](../machines/linux/doctor/README.en.md) |
| Poison | FreeBSD | Medium | LFI in `browse.php`, base64 in `pwdbackup.txt`, VNC as root with `secret.zip` | [Ver](../machines/freebsd/poison/README.md) | [EN](../machines/freebsd/poison/README.en.md) |
| SolidState | Linux | Medium | Apache James con credenciales por defecto, cron escribible | [ES](../machines/linux/solidstate/README.md) | [Ver](../machines/linux/solidstate/README.en.md) |
| DevOops | Linux | Medium | XXE en la subida de XML y clave de root en el historial de git | [ES](../machines/linux/devoops/README.md) | [Ver](../machines/linux/devoops/README.en.md) |
| Frolic | Linux | Easy | Client-side login, PlaySMS 1.4 CSV upload, SUID `rop` ret2libc | [Ver](../machines/linux/frolic/README.md) | [EN](../machines/linux/frolic/README.en.md) |
| Sea | Linux | Easy | WonderCMS CVE-2023-41425, cracked hash, command injection on 8080 | [Ver](../machines/linux/sea/README.md) | [EN](../machines/linux/sea/README.en.md) |
| Devel | Windows | Easy | Writable anonymous FTP over IIS, ASPX webshell, MS10-015 / `SeImpersonate` | [Ver](../machines/windows/devel/README.md) | [EN](../machines/windows/devel/README.en.md) |
| Fluffy | Windows | Easy | CVE-2025-24071, shadow credentials, ADCS ESC16 | [Ver](../machines/windows/fluffy/README.md) | [EN](../machines/windows/fluffy/README.en.md) |
| Garfield | Windows | Hard | RODC, KeyList golden ticket, secretsdump, pass-the-hash | [Ver](../machines/windows/garfield/README.md) | [EN](../machines/windows/garfield/README.en.md) |
| Academy | Linux | Easy | Roleid → Laravel CVE-2018-15133 via `APP_KEY`, `.env` and `composer` under sudo | [ES](../machines/linux/academy/README.md) | [Ver](../machines/linux/academy/README.en.md) |
| Apocalyst | Linux | Medium | WordPress, `cewl` and `steghide`, hydra, PHP plugin and a writable `/etc/passwd` | [ES](../machines/linux/apocalyst/README.md) | [Ver](../machines/linux/apocalyst/README.en.md) |
| OpenAdmin | Linux | Easy | OpenNetAdmin 18.1.1, credential reuse, `ssh2john` and a `nano` escape | [ES](../machines/linux/openadmin/README.md) | [Ver](../machines/linux/openadmin/README.en.md) |
| Tabby | Linux | Easy | LFI to `tomcat-users.xml`, WAR via `manager/text`, `fcrackzip` and the `lxd` group | [ES](../machines/linux/tabby/README.md) | [Ver](../machines/linux/tabby/README.en.md) |
| Jerry | Windows | Easy | Tomcat 7 with default credentials, WAR via `/manager/text` and a direct SYSTEM shell | [ES](../machines/windows/jerry/README.md) | [Ver](../machines/windows/jerry/README.en.md) |
| Chatterbox | Windows | Medium | AChat 0.150 buffer overflow (EDB 36025) and AutoLogon credentials in the registry | [ES](../machines/windows/chatterbox/README.md) | [Ver](../machines/windows/chatterbox/README.en.md) |
| Heist | Windows | Easy | Cisco config with type 7 and type 5, WinRM spray and `procdump` on Firefox | [ES](../machines/windows/heist/README.md) | [Ver](../machines/windows/heist/README.en.md) |
| Valentine | Linux | Easy | Heartbleed leaks an RSA key passphrase, SSH and a root `tmux` socket | [ES](../machines/linux/valentine/README.md) | [Ver](../machines/linux/valentine/README.en.md) |
| Shocker | Linux | Easy | Shellshock in a CGI (`user.sh`) and `sudo perl` via GTFOBins | [ES](../machines/linux/shocker/README.md) | [Ver](../machines/linux/shocker/README.en.md) |
| SwagShop | Linux | Easy | Magento with the Shoplift SQLi, Connect Manager and `sudo vi` | [ES](../machines/linux/swagshop/README.md) | [Ver](../machines/linux/swagshop/README.en.md) |
| Networked | Linux | Easy | Source-code backup, double extension, injectable cron and unquoted `sudo` | [ES](../machines/linux/networked/README.md) | [Ver](../machines/linux/networked/README.en.md) |
| Sense | FreeBSD | Easy | pfSense 2.1.3 with default credentials and CVE-2014-4688 as root | [ES](../machines/freebsd/sense/README.md) | [Ver](../machines/freebsd/sense/README.en.md) |
| Legacy | Windows | Easy | MS08-067 over SMBv1 on Windows XP | [ES](../machines/windows/legacy/README.md) | [Ver](../machines/windows/legacy/README.en.md) |
| Sunday | Solaris | Easy | `finger` user enumeration, cracked shadow and `sudo wget` | [ES](../machines/solaris/sunday/README.md) | [Ver](../machines/solaris/sunday/README.en.md) |
| Lame | Linux | Easy | Samba `usermap_script` (CVE-2007-2447) for direct root; `distcc` and `vsftpd` as alternates | [ES](../machines/linux/lame/README.md) | [Ver](../machines/linux/lame/README.en.md) |
| Optimum | Windows | Easy | Rejetto HFS 2.3 (CVE-2014-6287) and MS16-032 up to SYSTEM | [ES](../machines/windows/optimum/README.md) | [Ver](../machines/windows/optimum/README.en.md) |
| Sau | Linux | Easy | Request Baskets SSRF into Maltrail, then `sudo systemctl` pager escape | [ES](../machines/linux/sau/README.md) | [Ver](../machines/linux/sau/README.en.md) |
| Nineveh | Linux | Medium | phpLiteAdmin + LFI, port knocking and chkrootkit 0.49 as root | [ES](../machines/linux/nineveh/README.md) | [Ver](../machines/linux/nineveh/README.en.md) |
| Jeeves | Windows | Medium | Unauthenticated Jenkins, KeePass, pass-the-hash and a flag in an NTFS stream | [ES](../machines/windows/jeeves/README.md) | [Ver](../machines/windows/jeeves/README.en.md) |
| CozyHosting | Linux | Easy | Actuator session leak, panel command injection, PostgreSQL and `sudo ssh` | [ES](../machines/linux/cozyhosting/README.md) | [Ver](../machines/linux/cozyhosting/README.en.md) |
| BoardLight | Linux | Easy | Dolibarr 17.0.0 with defaults, CVE-2023-30253 and an Enlightenment SUID | [ES](../machines/linux/boardlight/README.md) | [Ver](../machines/linux/boardlight/README.en.md) |
| Busqueda | Linux | Easy | Searchor `eval()`, a `.git` with credentials, Gitea and the relative `full-checkup.sh` | [ES](../machines/linux/busqueda/README.md) | [Ver](../machines/linux/busqueda/README.en.md) |
| Soccer | Linux | Easy | Default Tiny File Manager, blind WebSocket SQLi and `doas` with `dstat` | [ES](../machines/linux/soccer/README.md) | [Ver](../machines/linux/soccer/README.en.md) |
| Timelapse | Windows | Easy | Anonymous SMB, PFX, PowerShell history and LAPS up to Administrator | [ES](../machines/windows/timelapse/README.md) | [Ver](../machines/windows/timelapse/README.en.md) |
| Cicada | Windows | Easy | Guest SMB, onboarding password, spray and `SeBackupPrivilege` | [Ver](../machines/windows/cicada/README.md) | [EN](../machines/windows/cicada/README.en.md) |
| Support | Windows | Easy | Reversing `UserInfo.exe`, password in `info`, GenericAll over the DC and RBCD | [Ver](../machines/windows/support/README.md) | [EN](../machines/windows/support/README.en.md) |
| Administrator | Windows | Medium | ACL chain to FTP, `.psafe3`, targeted kerberoasting and DCSync | [Ver](../machines/windows/administrator/README.md) | [EN](../machines/windows/administrator/README.en.md) |
| Escape | Windows | Medium | PDF with MSSQL credentials, `xp_dirtree` and ADCS ESC1 | [Ver](../machines/windows/escape/README.md) | [EN](../machines/windows/escape/README.en.md) |
| Pilgrimage | Linux | Easy | `/.git`, ImageMagick CVE-2022-44268 and binwalk CVE-2022-4510 | [Ver](../machines/linux/pilgrimage/README.md) | [EN](../machines/linux/pilgrimage/README.en.md) |
| MakeSense | Linux | Medium | Season 11: admin-bot XSS, forged AES-GCM, malicious plugin and OCR as root | [Ver](../machines/linux/makesense/README.md) | [EN](../machines/linux/makesense/README.en.md) |
| Cascade | Windows | Medium | Anonymous LDAP, `cascadeLegacyPwd`, reversible VNC and AD Recycle Bin | [Ver](../machines/windows/cascade/README.md) | [EN](../machines/windows/cascade/README.en.md) |
| Traceback | Linux | Easy | SmEvK web shell with default credentials, `luvit` via sudo and writable MOTD | [Ver](../machines/linux/traceback/README.md) | [EN](../machines/linux/traceback/README.en.md) |
| Craft | Linux | Easy | `eval()` in Flask, Gogs history, cleartext MySQL and a Vault OTP | [Ver](../machines/linux/craft/README.md) | [EN](../machines/linux/craft/README.en.md) |
| Book | Linux | Medium | SQL truncation on signup, XSS in the PDF and a `logrotate` race | [Ver](../machines/linux/book/README.md) | [EN](../machines/linux/book/README.en.md) |
| Querier | Windows | Medium | Credentials in a macro, `xp_dirtree`, NetNTLMv2 and GPP | [Ver](../machines/windows/querier/README.md) | [EN](../machines/windows/querier/README.en.md) |
| Remote | Windows | Medium | NFS with the Umbraco backup, SHA1, XSLT RCE and TeamViewer | [Ver](../machines/windows/remote/README.md) | [EN](../machines/windows/remote/README.en.md) |
| Luke | FreeBSD | Medium | Cleartext `config.php`, an API with JWT and Ajenti as root | [Ver](../machines/freebsd/luke/README.md) | [EN](../machines/freebsd/luke/README.en.md) |

## Pending

1 retired machine with material located but no writeup yet.

**Linux:** DevArea.


**Not yet classified:** MonitorsFour, Pirate and Pterodactyl.

## PDF dump

A Spanish-language dump with 164 machine directories, 140 of them holding PDFs (448 PDF and 73 ZIP, ~950 MB). 23 are empty: Ariekei, Bastard, Beep, Brainfuck, Charon, CrimeStoppers, Feline, FluxCapacitor, Fulcrum, Holiday, Inception, Jail, Jeeves, Joker, Lame, Mantis, Minion, Name, Optimum, Shrek, SolidState, Tally, and Smasher (a ZIP only). It is not Markdown: useful as a technique reference, not as text.

## Classification notes

- **PingPong is Insane**, not Hard: the original index files it as Hard, but the weekly drop and several independent sources rate it Insane (Windows, two AD forests).
- **`ref.`** means reference note: the machine was not completed on this profile, so there is no achievement link and no flags are published.
- The cross-inventory of the collections (coverage, duplicates, licences) stays outside the repo in a git-ignored local directory, since it holds third-party material.

## Starting Point (available)

These 25 machines are not retired —they are still available on the platform— but they are catalogued here so the index covers all 121 notes in the repository. Details, with tier and service, live in the section index.

| Machine | OS | Difficulty | Main technique | ES | EN |
|---|---|---|---|---|---|
| Meow | Linux | Very Easy | Telnet with a passwordless `root` | [Ver](../machines/starting-point/meow/README.md) | [EN](../machines/starting-point/meow/README.en.md) |
| Fawn | Linux | Very Easy | Anonymous FTP and `get flag.txt` | [Ver](../machines/starting-point/fawn/README.md) | [EN](../machines/starting-point/fawn/README.en.md) |
| Dancing | Windows | Very Easy | Null SMB and the `WorkShares` share | [Ver](../machines/starting-point/dancing/README.md) | [EN](../machines/starting-point/dancing/README.en.md) |
| Redeemer | Linux | Very Easy | Redis without `AUTH` | [Ver](../machines/starting-point/redeemer/README.md) | [EN](../machines/starting-point/redeemer/README.en.md) |
| Explosion | Windows | Very Easy | RDP with a blank `Administrator` | [Ver](../machines/starting-point/explosion/README.md) | [EN](../machines/starting-point/explosion/README.en.md) |
| Preignition | Linux | Very Easy | `/admin.php` with `admin:admin` | [Ver](../machines/starting-point/preignition/README.md) | [EN](../machines/starting-point/preignition/README.en.md) |
| Mongod | Linux | Very Easy | MongoDB without `--auth` | [Ver](../machines/starting-point/mongod/README.md) | [EN](../machines/starting-point/mongod/README.en.md) |
| Synced | Linux | Very Easy | Anonymous rsync on 873 | [Ver](../machines/starting-point/synced/README.md) | [EN](../machines/starting-point/synced/README.en.md) |
| Sequel | Linux | Very Easy | Passwordless MySQL `root` | [Ver](../machines/starting-point/sequel/README.md) | [EN](../machines/starting-point/sequel/README.en.md) |
| Appointment | Linux | Very Easy | Login SQLi `admin' or '1'='1'#` | [Ver](../machines/starting-point/appointment/README.md) | [EN](../machines/starting-point/appointment/README.en.md) |
| Crocodile | Linux | Very Easy | Anonymous FTP with user lists | [Ver](../machines/starting-point/crocodile/README.md) | [EN](../machines/starting-point/crocodile/README.en.md) |
| Responder | Windows | Very Easy | LFI to UNC, NetNTLMv2 and WinRM | [Ver](../machines/starting-point/responder/README.md) | [EN](../machines/starting-point/responder/README.en.md) |
| Three | Linux | Very Easy | Unauthenticated S3 bucket and webshell | [Ver](../machines/starting-point/three/README.md) | [EN](../machines/starting-point/three/README.en.md) |
| Ignition | Linux | Very Easy | Magento with `admin:qwerty123` | [Ver](../machines/starting-point/ignition/README.md) | [EN](../machines/starting-point/ignition/README.en.md) |
| Bike | Linux | Very Easy | Handlebars SSTI as root | [Ver](../machines/starting-point/bike/README.md) | [EN](../machines/starting-point/bike/README.en.md) |
| Funnel | Linux | Very Easy | SSH spray and PostgreSQL tunnel | [Ver](../machines/starting-point/funnel/README.md) | [EN](../machines/starting-point/funnel/README.en.md) |
| Pennyworth | Linux | Very Easy | Jenkins `root:password` and Groovy | [Ver](../machines/starting-point/pennyworth/README.md) | [EN](../machines/starting-point/pennyworth/README.en.md) |
| Tactics | Windows | Very Easy | Null SMB and a blank `Administrator` | [Ver](../machines/starting-point/tactics/README.md) | [EN](../machines/starting-point/tactics/README.en.md) |
| Archetype | Windows | Very Easy | `prod.dtsConfig`, `xp_cmdshell`, psexec | [Ver](../machines/starting-point/archetype/README.md) | [EN](../machines/starting-point/archetype/README.en.md) |
| Oopsie | Linux | Very Easy | Cookie IDOR, upload and SUID | [Ver](../machines/starting-point/oopsie/README.md) | [EN](../machines/starting-point/oopsie/README.en.md) |
| Vaccine | Linux | Very Easy | `backup.zip`, SQLi and `sudo vi` | [Ver](../machines/starting-point/vaccine/README.md) | [EN](../machines/starting-point/vaccine/README.en.md) |
| Unified | Linux | Very Easy | Log4Shell on UniFi and MongoDB | [Ver](../machines/starting-point/unified/README.md) | [EN](../machines/starting-point/unified/README.en.md) |
| Included | Linux | Very Easy | LFI, TFTP and the `lxd` group | [Ver](../machines/starting-point/included/README.md) | [EN](../machines/starting-point/included/README.en.md) |
| Markup | Windows | Very Easy | XXE to `id_rsa` and `job.bat` | [Ver](../machines/starting-point/markup/README.md) | [EN](../machines/starting-point/markup/README.en.md) |
| Base | Linux | Very Easy | `strcmp` with arrays and `sudo find` | [Ver](../machines/starting-point/base/README.md) | [EN](../machines/starting-point/base/README.en.md) |
