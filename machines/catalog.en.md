# Retired machine catalogue

**English** | [🇪🇸 Español](catalog.md)

Reference notes for machines used to study techniques. The main table covers **retired** boxes; at the end there is a section with the 25 **Starting Point** machines, which are still available on the platform. Rows marked `ref.` were not played on this profile: they are study material, not an achievement, and carry no flags or credentials. Machines that were played live live in `machines/linux/`, `machines/windows/` or `machines/starting-point/` and appear in the main index.

## Written

| Machine | OS | Difficulty | Main technique | ES | EN |
|---|---|---|---|---|---|
| Absolute | Windows | Insane | AS-REP, shadow credentials, KrbRelay and DCSync | [ES](../machines/windows/absolute/README.md) | [Ver](../machines/windows/absolute/README.en.md) |
| Academy | Linux | Easy | Roleid → Laravel CVE-2018-15133 via `APP_KEY`, `.env` and `composer` under sudo | [ES](../machines/linux/academy/README.md) | [Ver](../machines/linux/academy/README.en.md) |
| Access | Windows | Easy | Anonymous FTP, MDB, Outlook PST, telnet and `runas /savecred` | [ES](../machines/windows/access/README.md) | [EN](../machines/windows/access/README.en.md) |
| Active | Windows | Easy | GPP in SYSVOL, Kerberoasting `Administrator` | [ES](../machines/windows/active/README.md) | [Ver](../machines/windows/active/README.en.md) |
| Acute | Windows | Hard | PSWA, DOCX metadata, Meterpreter with a Defender bypass and `keepmeon.bat` to Site Admin | [See](../machines/windows/acute/README.md) | [EN](../machines/windows/acute/README.en.md) |
| Administrator | Windows | Medium | ACL chain to FTP, `.psafe3`, targeted kerberoasting and DCSync | [Ver](../machines/windows/administrator/README.md) | [EN](../machines/windows/administrator/README.en.md) |
| Admirer | Linux | Easy | Adminer 4.6.2, LFI via rogue MySQL, `PYTHONPATH` | [ES](../machines/linux/admirer/README.md) | [Ver](../machines/linux/admirer/README.en.md) |
| AdmirerToo | Linux | Hard | Adminer SSRF, OpenTSDB, OpenCats and fail2ban | [ES](../machines/linux/admirertoo/README.md) | [EN](../machines/linux/admirertoo/README.en.md) |
| Aero | Windows | Medium | ThemeBleed CVE-2023-38146 and CLFS CVE-2023-28252 | [ES](../machines/windows/aero/README.md) | [EN](../machines/windows/aero/README.en.md) |
| Agile | Linux | Medium | Flask debug PIN, Chrome debug and sudoedit CVE-2023-22809 | [ES](../machines/linux/agile/README.md) | [EN](../machines/linux/agile/README.en.md) |
| AI | Linux | Medium | SQLi in audio transcription and Tomcat JDWP as root | [ES](../machines/linux/ai/README.md) | [Ver](../machines/linux/ai/README.en.md) |
| AirTouch | Linux | Medium | WPA2, PEAP Evil Twin, VPN pivot | [ES](../machines/linux/airtouch/README.md) | [Ver](../machines/linux/airtouch/README.en.md) |
| Alert | Linux | Easy | Markdown XSS, file read, `.htpasswd` and PHP cron | [ES](../machines/linux/alert/README.md) | [EN](../machines/linux/alert/README.en.md) |
| Ambassador | Linux | Medium | Grafana CVE-2021-43798, `grafana.db` and Consul | [Ver](../machines/linux/ambassador/README.md) | [EN](../machines/linux/ambassador/README.en.md) |
| Analytics | Linux | Easy | Metabase CVE-2023-38646, container credentials and overlayfs | [Ver](../machines/linux/analytics/README.md) | [EN](../machines/linux/analytics/README.en.md) |
| Anubis | Windows | Insane | ASP, Jamovi, ADCS ESC and PKINIT | [View](../machines/windows/anubis/README.en.md) | [ES](../machines/windows/anubis/README.md) |
| Apocalyst | Linux | Medium | WordPress, `cewl` and `steghide`, hydra, PHP plugin and a writable `/etc/passwd` | [ES](../machines/linux/apocalyst/README.md) | [Ver](../machines/linux/apocalyst/README.en.md) |
| Apt | Windows | Insane | IPv6/RPC, `ntds.dit` backup, NTLMv1 and RoguePotato/relay | [Ver](../machines/windows/apt/README.md) | [EN](../machines/windows/apt/README.en.md) |
| Aragog | Linux | Medium | Anonymous FTP, XXE in `hosts.php`, `florian` SSH key and WordPress credentials to root | [ES](../machines/linux/aragog/README.md) | [Ver](../machines/linux/aragog/README.en.md) |
| Arctic | Windows | Easy | ColdFusion 8 + FCKeditor, JuicyPotato | [ES](../machines/windows/arctic/README.md) | [Ver](../machines/windows/arctic/README.en.md) |
| Ariekei | Linux | Insane | vhost Shellshock, ImageTragick and Dockerfiles | [View](../machines/linux/ariekei/README.en.md) | [ES](../machines/linux/ariekei/README.md) |
| Arkham | Windows | Medium | LUKS, JSF ViewState and Java deserialization | [ES](../machines/windows/arkham/README.md) | [EN](../machines/windows/arkham/README.en.md) |
| Armageddon | Linux | Easy | Drupal 7.56, Drupalgeddon2, snap hook | [ES](../machines/linux/armageddon/README.md) | [Ver](../machines/linux/armageddon/README.en.md) |
| Artificial | Linux | Easy | TensorFlow Lambda, Backrest backup and root hooks | [View](../machines/linux/artificial/README.md) | [EN](../machines/linux/artificial/README.en.md) |
| Atom | Windows | Medium | Electron updater, writable SMB share and PortableKanban in Redis | [View](../machines/windows/atom/README.en.md) | [ES](../machines/windows/atom/README.md) |
| Attended | OpenBSD | Insane | OpenSMTPD, Vim modeline and ROP | [ES](../machines/openbsd/attended/README.md) | [EN](../machines/openbsd/attended/README.en.md) |
| Authority | Windows | Medium | Anonymous SMB, Ansible Vault, PWM, ESC1 (`CorpVPN`) and PassTheCert | [ES](../machines/windows/authority/README.md) | [Ver](../machines/windows/authority/README.en.md) |
| Awkward | Linux | Medium | Cookie bypass, SSRF, `awk` injection, `xpad` backup and a symlink into root's mail | [See](../machines/linux/awkward/README.md) | [EN](../machines/linux/awkward/README.en.md) |
| Axlle | Windows | Hard | XLL, `.url` files, PowerShell history and LOLBIN | [ES](../machines/windows/axlle/README.md) | [EN](../machines/windows/axlle/README.en.md) |
| Baby | Windows | Easy | LDAP credential, spray, `Backup Operators` and NTDS dump | [Ver](../machines/windows/baby/README.md) | [EN](../machines/windows/baby/README.en.md) |
| Backdoor | Linux | Easy | WordPress plugin traversal, `gdbserver` and root `screen` | [View](../machines/linux/backdoor/README.en.md) | [ES](../machines/linux/backdoor/README.md) |
| Bank | Linux | Easy | AXFR, `302` to `200`, `.htb` upload, SUID | [ES](../machines/linux/bank/README.md) | [Ver](../machines/linux/bank/README.en.md) |
| Bankrobber | Windows | Insane | XSS stealing admin cookies, SQLi and a `bankv2` overflow | [ES](../machines/windows/bankrobber/README.md) | [Ver](../machines/windows/bankrobber/README.en.md) |
| Bart | Windows | Medium | IIS, vhosts, log poisoning and autologon | [ES](../machines/windows/bart/README.md) | [EN](../machines/windows/bart/README.en.md) |
| Bashed | Linux | Easy | `phpbash` web shell, `sudo -u`, root cron | [ES](../machines/linux/bashed/README.md) | [Ver](../machines/linux/bashed/README.en.md) |
| Bastard | Windows | Medium | Drupalgeddon2 and JuicyPotato | [ES](../machines/windows/bastard/README.md) | [Ver](../machines/windows/bastard/README.en.md) |
| Bastion | Windows | Easy | SMB backup with VHDX, SAM/SYSTEM, mRemoteNG | [ES](../machines/windows/bastion/README.md) | [Ver](../machines/windows/bastion/README.en.md) |
| Beep | Linux | Easy | Elastix LFI, CVE-2012-4869, interactive `nmap` | [ES](../machines/linux/beep/README.md) | [Ver](../machines/linux/beep/README.en.md) |
| BigBang | Linux | Hard | BuddyForms, PHP filter chains and CVE-2024-2961 | [View](../machines/linux/bigbang/README.md) | [EN](../machines/linux/bigbang/README.en.md) |
| BigHead | Windows | Insane | Dev vhost, GitHub backup, egghunter buffer overflow, TestLink and KeePass with an ADS keyfile | [View](../machines/windows/bighead/README.en.md) | [ES](../machines/windows/bighead/README.md) |
| Bitlab | Linux | Medium | GitLab, webshell, PostgreSQL tunnel and `RemoteConnection.exe` reversing | [ES](../machines/linux/bitlab/README.md) | [EN](../machines/linux/bitlab/README.en.md) |
| Bizness | Linux | Easy | Apache OFBiz CVE-2023-49070 and Derby hash | [View](../machines/linux/bizness/README.en.md) | [ES](../machines/linux/bizness/README.md) |
| Blackfield | Windows | Hard | AS-REP, volcado de lsass, SeBackupPrivilege, NTDS | [ES](../machines/windows/blackfield/README.md) | [Ver](../machines/windows/blackfield/README.en.md) |
| Blazorized | Windows | Hard | Blazor JWT, SQLi and ACL chain to DCSync | [View](../machines/windows/blazorized/README.md) | [EN](../machines/windows/blazorized/README.en.md) |
| BlockBlock | Linux | Hard | Chat XSS, Ethereum JSON-RPC and `forge`/`pacman` | [View](../machines/linux/blockblock/README.en.md) | [ES](../machines/linux/blockblock/README.md) |
| Blocky | Linux | Easy | credentials in a JAR, reuse, `sudo ALL` | [ES](../machines/linux/blocky/README.md) | [Ver](../machines/linux/blocky/README.en.md) |
| Blue | Windows | Easy | MS17-010 EternalBlue | [ES](../machines/windows/blue/README.md) | [Ver](../machines/windows/blue/README.en.md) |
| Blunder | Linux | Easy | Bludit, brute-force bypass, `sudo -u#-1` | [ES](../machines/linux/blunder/README.md) | [Ver](../machines/linux/blunder/README.en.md) |
| Blurry | Linux | Medium | ClearML pickle and Fickling evasion in PyTorch | [View](../machines/linux/blurry/README.md) | [EN](../machines/linux/blurry/README.en.md) |
| BoardLight | Linux | Easy | Dolibarr 17.0.0 with defaults, CVE-2023-30253 and an Enlightenment SUID | [ES](../machines/linux/boardlight/README.md) | [Ver](../machines/linux/boardlight/README.en.md) |
| Bolt | Linux | Medium | Docker layers with secrets, Flask SSTI and Passbolt | [View](../machines/linux/bolt/README.en.md) | [ES](../machines/linux/bolt/README.md) |
| Book | Linux | Medium | SQL truncation on signup, XSS in the PDF and a `logrotate` race | [Ver](../machines/linux/book/README.md) | [EN](../machines/linux/book/README.en.md) |
| Bookworm | Linux | Insane | XSS, IDOR, ZIP traversal and PostScript in `genlabel` | [ES](../machines/linux/bookworm/README.md) | [Ver](../machines/linux/bookworm/README.en.md) |
| Bounty | Windows | Easy | `web.config` on IIS, `SeImpersonate`, JuicyPotato | [ES](../machines/windows/bounty/README.md) | [Ver](../machines/windows/bounty/README.en.md) |
| BountyHunter | Linux | Easy | XXE, password in `db.php` and Python eval with sudo | [View](../machines/linux/bountyhunter/README.en.md) | [ES](../machines/linux/bountyhunter/README.md) |
| Brainfuck | Linux | Insane | WordPress, bypass, Vigenère and `lxd` | [ES](../machines/linux/brainfuck/README.md) | [EN](../machines/linux/brainfuck/README.en.md) |
| Breadcrumbs | Windows | Hard | PHP traversal, forged cookie, SQLite WAL and AES SQLi | [View](../machines/windows/breadcrumbs/README.en.md) | [ES](../machines/windows/breadcrumbs/README.md) |
| Broker | Linux | Easy | ActiveMQ CVE-2023-46604, Spring XML and `ld.so.preload` via `sudo nginx` | [Ver](../machines/linux/broker/README.md) | [EN](../machines/linux/broker/README.en.md) |
| BroScience | Linux | Medium | `img.php?path=` LFI, double URL-encoding, `AvatarInterface` and hashcat `-m 20` | [Ver](../machines/linux/broscience/README.md) | [EN](../machines/linux/broscience/README.en.md) |
| Browsed | Linux | Medium | Chrome logs, SSRF extension and `__pycache__` poisoning | [View](../machines/linux/browsed/README.en.md) | [ES](../machines/linux/browsed/README.md) |
| Bucket | Linux | Medium | Writable S3 bucket, DynamoDB and root PDF generator | [View](../machines/linux/bucket/README.en.md) | [ES](../machines/linux/bucket/README.md) |
| Buff | Windows | Easy | Subida sin autenticacion, CloudMe 1.11.2 | [ES](../machines/windows/buff/README.md) | [Ver](../machines/windows/buff/README.en.md) |
| Build | Linux | Medium | Jenkins backup over rsync, Gitea pipeline and rlogin | [Ver](../machines/linux/build/README.md) | [EN](../machines/linux/build/README.en.md) |
| Builder | Linux | Medium | Jenkins CVE-2024-23897, bcrypt hash and SSH credential via SSH Agent | [Ver](../machines/linux/builder/README.md) | [EN](../machines/linux/builder/README.en.md) |
| Busqueda | Linux | Easy | Searchor `eval()`, a `.git` with credentials, Gitea and the relative `full-checkup.sh` | [ES](../machines/linux/busqueda/README.md) | [Ver](../machines/linux/busqueda/README.en.md) |
| Cache | Linux | Medium | OpenEMR auth bypass/SQLi, bcrypt, authenticated RCE and memcached/docker | [Ver](../machines/linux/cache/README.md) | [EN](../machines/linux/cache/README.en.md) |
| Calamity | Linux | Hard | Arbitrary PHP, audio steganography and SUID overflow | [View](../machines/linux/calamity/README.en.md) | [ES](../machines/linux/calamity/README.md) |
| Canape | Linux | Medium | Exposed `.git`, Flask pickle, CVE-2017-12635 and `sudo pip` | [ES](../machines/linux/canape/README.md) | [Ver](../machines/linux/canape/README.en.md) |
| Cap | Linux | Easy | IDOR, pcap, `cap_setuid` | [ES](../machines/linux/cap/README.md) | [Ver](../machines/linux/cap/README.en.md) |
| Caption | Linux | Hard | h2c smuggling, cookie theft, CopyParty and log handler | [View](../machines/linux/caption/README.en.md) | [ES](../machines/linux/caption/README.md) |
| Carpediem | Linux | Hard | Mass assignment, webshell, Trudesk, `tcpdump` and CVE-2022-0492 | [Ver](../machines/linux/carpediem/README.md) | [EN](../machines/linux/carpediem/README.en.md) |
| Carrier | Linux | Medium | SNMP, router RCE, BGP hijack, FTP capture and root | [View](../machines/linux/carrier/README.en.md) | [ES](../machines/linux/carrier/README.md) |
| Cascade | Windows | Medium | Anonymous LDAP, `cascadeLegacyPwd`, reversible VNC and AD Recycle Bin | [Ver](../machines/windows/cascade/README.md) | [EN](../machines/windows/cascade/README.en.md) |
| Cat | Linux | Medium | `.git`, XSS, `ATTACH` SQLi and Gitea CVE-2024-6886 | [View](../machines/linux/cat/README.en.md) | [ES](../machines/linux/cat/README.md) |
| Catch | Linux | Medium | APK, secrets in Gitea and Let's Chat | [View](../machines/linux/catch/README.en.md) | [ES](../machines/linux/catch/README.md) |
| CCTV | Linux | Hard | ZoneMinder CVE-2024-51482, bcrypt, `tcpdump` and motionEye CVE-2025-60787 | [Ver](../machines/linux/cctv/README.md) | [EN](../machines/linux/cctv/README.en.md) |
| Celestial | Linux | Medium | Base64 cookie with `node-serialize`, RCE as `sun` and a cron restoring the script | [ES](../machines/linux/celestial/README.md) | [Ver](../machines/linux/celestial/README.en.md) |
| Cerberus | Windows | Hard | IcingaWeb2, Firejail, SSSD and ADSelfService Plus | [View](../machines/windows/cerberus/README.en.md) | [ES](../machines/windows/cerberus/README.md) |
| Cereal | Windows | Hard | `.git`, forged JWT, .NET deserialization and GenericPotato | [View](../machines/windows/cereal/README.en.md) | [ES](../machines/windows/cereal/README.md) |
| Certificate | Windows | Hard | ADCS ESC3, Golden Certificate and EFS | [Ver](../machines/windows/certificate/README.md) | [EN](../machines/windows/certificate/README.en.md) |
| Certified | Windows | Medium | `WriteOwner`/`GenericAll` and AD CS ESC9 | [Ver](../machines/windows/certified/README.md) | [EN](../machines/windows/certified/README.en.md) |
| Chaffinch | Windows | Medium | GeoServer CVE-2024-36401 and CSC service abuse | [ES](../machines/windows/chaffinch/README.md) | [EN](../machines/windows/chaffinch/README.en.md) |
| Chainsaw | Linux | Insane | Solidity/FTP, Ethereum 9810, `setDomain` injection, IPFS and slack space | [Ver](../machines/linux/chainsaw/README.md) | [EN](../machines/linux/chainsaw/README.en.md) |
| Chaos | Linux | Medium | WordPress, pdfTeX `\write18`, `rbash` and Firefox credentials | [ES](../machines/linux/chaos/README.md) | [Ver](../machines/linux/chaos/README.en.md) |
| Charon | Linux | Hard | Filter-bypass SQLi, small-modulus RSA and SUID `supershell` | [ES](../machines/linux/charon/README.md) | [Ver](../machines/linux/charon/README.en.md) |
| Chatterbox | Windows | Medium | AChat 0.150 buffer overflow (EDB 36025) and AutoLogon credentials in the registry | [ES](../machines/windows/chatterbox/README.md) | [Ver](../machines/windows/chatterbox/README.en.md) |
| Checker | Linux | Hard | Teampass CVE-2023-1545, BookStack CVE-2023-6199 and a race in `check_leak` | [View](../machines/linux/checker/README.en.md) | [ES](../machines/linux/checker/README.md) |
| Checkpoint | Windows | Medium | AD Recycle Bin, VS Code extension and `vmkatz` | [View](../machines/windows/checkpoint/README.en.md) | [ES](../machines/windows/checkpoint/README.md) |
| Chemistry | Linux | Easy | pymatgen CVE-2024-23346 and aiohttp traversal | [ES](../machines/linux/chemistry/README.md) | [Ver](../machines/linux/chemistry/README.en.md) |
| Cicada | Windows | Easy | Guest SMB, onboarding password, spray and `SeBackupPrivilege` | [Ver](../machines/windows/cicada/README.md) | [EN](../machines/windows/cicada/README.en.md) |
| Clicker | Linux | Medium | NFS source leak, mass assignment, webshell and `PERL5OPT` | [ES](../machines/linux/clicker/README.md) | [Ver](../machines/linux/clicker/README.en.md) |
| Cobblestone | Linux | Insane | Second-order SQLi, Twig SSTI, Cobbler | [ES](../machines/linux/cobblestone/README.md) | [Ver](../machines/linux/cobblestone/README.en.md) |
| Code | Linux | Easy | Python sandbox escape, bcrypt, `backy.sh` | [ES](../machines/linux/code/README.md) | [Ver](../machines/linux/code/README.en.md) |
| Coder | Windows | Insane | SMB, KeePass, TeamCity and Certifried | [View](../machines/windows/coder/README.en.md) | [ES](../machines/windows/coder/README.md) |
| Codify | Linux | Easy | vm2 3.9.16, SQLite bcrypt and a glob in `mysql-backup.sh` | [View](../machines/linux/codify/README.en.md) | [ES](../machines/linux/codify/README.md) |
| Compiled | Windows | Medium | Git CVE-2024-32002, Gitea hashes and Visual Studio | [View](../machines/windows/compiled/README.en.md) | [ES](../machines/windows/compiled/README.md) |
| Compromised | Linux | Hard | LiteCart backup, MySQL UDF, `strace` and PAM | [View](../machines/linux/compromised/README.en.md) | [ES](../machines/linux/compromised/README.md) |
| Conceal | Windows | Hard | SNMP/IPsec, anonymous FTP webshell and JuicyPotato | [Ver](../machines/windows/conceal/README.md) | [EN](../machines/windows/conceal/README.en.md) |
| Control | Windows | Hard | `X-Forwarded-For`, SQLi with `FILE`, IIS webshell and service `ImagePath` | [Ver](../machines/windows/control/README.md) | [EN](../machines/windows/control/README.en.md) |
| Conversor | Linux | Medium | `os.path.join`, script cron and `needrestart` | [ES](../machines/linux/conversor/README.md) | [Ver](../machines/linux/conversor/README.en.md) |
| CozyHosting | Linux | Easy | Actuator session leak, panel command injection, PostgreSQL and `sudo ssh` | [ES](../machines/linux/cozyhosting/README.md) | [Ver](../machines/linux/cozyhosting/README.en.md) |
| Craft | Linux | Easy | `eval()` in Flask, Gogs history, cleartext MySQL and a Vault OTP | [Ver](../machines/linux/craft/README.md) | [EN](../machines/linux/craft/README.en.md) |
| Crafty | Windows | Easy | Minecraft Log4Shell, plugin JAR and RCON | [View](../machines/windows/crafty/README.md) | [EN](../machines/windows/crafty/README.en.md) |
| CrimeStoppers | Linux | Hard | LFI with `php://filter`, `zip://` and the `rootme` Apache module | [ES](../machines/linux/crimestoppers/README.md) | [Ver](../machines/linux/crimestoppers/README.en.md) |
| Cronos | Linux | Medium | AXFR, SQLi, command injection, `artisan` cron | [ES](../machines/linux/cronos/README.md) | [Ver](../machines/linux/cronos/README.en.md) |
| CrossFit | Linux | Insane | XSS, CSRF, FTP, `php-shellcommand` and cron symlink | [ES](../machines/linux/crossfit/README.md) | [Ver](../machines/linux/crossfit/README.en.md) |
| CrossFitTwo | OpenBSD | Insane | WebSocket SQLi, Node modules and Yubikey | [ES](../machines/openbsd/crossfittwo/README.md) | [EN](../machines/openbsd/crossfittwo/README.en.md) |
| CTF | Linux | Insane | LDAP injection, OTP and `7za` listfile | [ES](../machines/linux/ctf/README.md) | [Ver](../machines/linux/ctf/README.en.md) |
| Curling | Linux | Easy | Joomla backup, webshell and `curl` cron | [View](../machines/linux/curling/README.en.md) | [ES](../machines/linux/curling/README.md) |
| Cybermonday | Linux | Hard | Off-by-slash, JWT confusion, Redis SSRF and Docker | [ES](../machines/linux/cybermonday/README.md) | [Ver](../machines/linux/cybermonday/README.en.md) |
| Cypher | Linux | Medium | Cypher injection, APOC extension and `bbot` | [ES](../machines/linux/cypher/README.md) | [Ver](../machines/linux/cypher/README.en.md) |
| Dab | Linux | Hard | Memcached through a proxy, MD5 hashes and `ldconfig` | [ES](../machines/linux/dab/README.md) | [EN](../machines/linux/dab/README.en.md) |
| DarkCorp | Windows | Insane | RoundCube XSS, PostgreSQL, NTLM relay, shadow credentials and GPO | [ES](../machines/windows/darkcorp/README.md) | [Ver](../machines/windows/darkcorp/README.en.md) |
| DarkZero | Windows | Insane | MSSQL linked server, `xp_cmdshell`, CVE-2024-30088, forest trust and DC01 | [Ver](../machines/windows/darkzero/README.md) | [EN](../machines/windows/darkzero/README.en.md) |
| Data | Linux | Easy | Grafana CVE-2021-43798, PBKDF2 hash and privileged Docker | [ES](../machines/linux/data/README.md) | [Ver](../machines/linux/data/README.en.md) |
| Delivery | Linux | Easy | osTicket + Mattermost, bcrypt with rules | [ES](../machines/linux/delivery/README.md) | [Ver](../machines/linux/delivery/README.en.md) |
| Derailed | Linux | Insane | WASM overflow, admin XSS, `open()` pipe and OpenMediaVault | [ES](../machines/linux/derailed/README.md) | [Ver](../machines/linux/derailed/README.en.md) |
| DevArea | Linux | Medium | Anonymous FTP, CXF MTOM SSRF and double symlink via `syswatch` | [ES](../machines/linux/devarea/README.md) | [Ver](../machines/linux/devarea/README.en.md) |
| Devel | Windows | Easy | Writable anonymous FTP over IIS, ASPX webshell, MS10-015 / `SeImpersonate` | [Ver](../machines/windows/devel/README.md) | [EN](../machines/windows/devel/README.en.md) |
| Developer | Linux | Hard | Reverse tab-nabbing, Django pickle and privileged binary | [ES](../machines/linux/developer/README.md) | [Ver](../machines/linux/developer/README.en.md) |
| DevHub | Linux | Medium | MCPJam 1.4.2 CVE-2026-23744, Jupyter token and OPSMCP API as root | [ES](../machines/linux/devhub/README.md) | [Ver](../machines/linux/devhub/README.en.md) |
| DevOops | Linux | Medium | XXE en la subida de XML y clave de root en el historial de git | [ES](../machines/linux/devoops/README.md) | [Ver](../machines/linux/devoops/README.en.md) |
| Devvortex | Linux | Easy | Joomla API CVE-2023-23752, PHP template and `apport-cli` | [Ver](../machines/linux/devvortex/README.md) | [EN](../machines/linux/devvortex/README.en.md) |
| Devzat | Linux | Medium | Exposed `.git`, command injection, InfluxDB CVE-2019-20933 and root's SSH key | [See](../machines/linux/devzat/README.md) | [EN](../machines/linux/devzat/README.en.md) |
| Doctor | Linux | Easy | SSTI con Jinja2 en un vhost, Splunk 8.0.x | [ES](../machines/linux/doctor/README.md) | [Ver](../machines/linux/doctor/README.en.md) |
| Dog | Linux | Easy | Exposed `.git`, Backdrop module and `bee eval` | [ES](../machines/linux/dog/README.md) | [Ver](../machines/linux/dog/README.en.md) |
| Down | Linux | Easy | `curl`/`file://` SSRF, `nc` injection and `pswm` | [ES](../machines/linux/down/README.md) | [Ver](../machines/linux/down/README.en.md) |
| Download | Linux | Hard | `%2f` traversal, hash oracle, PostgreSQL and TIOCSTI | [ES](../machines/linux/download/README.md) | [Ver](../machines/linux/download/README.en.md) |
| Drive | Linux | Hard | IDOR, Gitea, `.7z` backups, Django hashes and setuid `doodleGrive-cli` with SQLite `load_extension` | [ES](../machines/linux/drive/README.md) | [Ver](../machines/linux/drive/README.en.md) |
| Driver | Windows | Easy | `.scf`/Responder, WinRM and PrintNightmare | [View](../machines/windows/driver/README.en.md) | [ES](../machines/windows/driver/README.md) |
| Dropzone | Windows | Hard | TFTP over `C:\`, WMI MOF and SYSTEM | [ES](../machines/windows/dropzone/README.md) | [Ver](../machines/windows/dropzone/README.en.md) |
| Dyplesher | Linux | Insane | Exposed `.git`, memcached binary SASL, Gogs, Bukkit plugin and RabbitMQ | [ES](../machines/linux/dyplesher/README.md) | [Ver](../machines/linux/dyplesher/README.en.md) |
| EarlyAccess | Linux | Hard | XSS, second-order SQLi, LFI/RCE, containers and an `arp` capability | [See](../machines/linux/earlyaccess/README.md) | [EN](../machines/linux/earlyaccess/README.en.md) |
| Editor | Linux | Medium | XWiki CVE-2025-24893 and NetData `ndsudo` | [ES](../machines/linux/editor/README.md) | [Ver](../machines/linux/editor/README.en.md) |
| Editorial | Linux | Easy | SSRF, exposed Git and GitPython CVE-2022-24439 | [ES](../machines/linux/editorial/README.md) | [Ver](../machines/linux/editorial/README.en.md) |
| Eighteen | Windows | Hard | `IMPERSONATE`, Werkzeug, CVE-2025-53779 | [ES](../machines/windows/eighteen/README.md) | [Ver](../machines/windows/eighteen/README.en.md) |
| Eloquia | Windows | Insane | AngularJS CSTI, OAuth, SQLite extension and AppDomainManager | [ES](../machines/windows/eloquia/README.md) | [Ver](../machines/windows/eloquia/README.en.md) |
| Environment | Linux | Medium | Laravel debug CVE-2024-52301, filemanager, GPG and `BASH_ENV` | [ES](../machines/linux/environment/README.md) | [EN](../machines/linux/environment/README.en.md) |
| Era | Linux | Medium | IDOR in backups, SSH module and a signed cron binary | [Ver](../machines/linux/era/README.md) | [EN](../machines/linux/era/README.en.md) |
| Escape | Windows | Medium | PDF with MSSQL credentials, `xp_dirtree` and ADCS ESC1 | [Ver](../machines/windows/escape/README.md) | [EN](../machines/windows/escape/README.en.md) |
| EscapeTwo | Windows | Easy | Excel, MSSQL, `WriteOwner` and ADCS ESC4 to ESC1 | [ES](../machines/windows/escapetwo/README.md) | [Ver](../machines/windows/escapetwo/README.en.md) |
| Ethereal | Windows | Insane | PasswordBox, DNS/OpenSSL, LNK and signed MSI | [ES](../machines/windows/ethereal/README.md) | [Ver](../machines/windows/ethereal/README.en.md) |
| Europa | Linux | Medium | Login SQLi, preg_replace /e and writable cron | [View](../machines/linux/europa/README.md) | [EN](../machines/linux/europa/README.en.md) |
| EvilCUPS | Linux | Medium | Attacker-controlled CUPS printer, Foomatic-RIP and spool | [View](../machines/linux/evilcups/README.en.md) | [ES](../machines/linux/evilcups/README.md) |
| Explore | Android | Easy | ES File Explorer CVE-2019-6447 and ADB | [ES](../machines/android/explore/README.md) | [EN](../machines/android/explore/README.en.md) |
| Expressway | Linux | Easy | IKE aggressive mode, reused PSK and `sudo` CVE-2025-32463 | [ES](../machines/linux/expressway/README.md) | [Ver](../machines/linux/expressway/README.en.md) |
| Extension | Linux | Hard | User API, accumulated resets, hash length extension and `docker.sock` | [ES](../machines/linux/extension/README.md) | [EN](../machines/linux/extension/README.en.md) |
| Facts | Linux | Easy | Camaleon CMS, MinIO, SSH key, `facter` | [ES](../machines/linux/facts/README.md) | [Ver](../machines/linux/facts/README.en.md) |
| Faculty | Linux | Medium | SQLi, mPDF file read, `meta-git` and GDB ptrace | [View](../machines/linux/faculty/README.en.md) | [ES](../machines/linux/faculty/README.md) |
| Falafel | Linux | Hard | Type juggling, PHP upload, framebuffer and debugfs | [View](../machines/linux/falafel/README.md) | [EN](../machines/linux/falafel/README.en.md) |
| Fatty | Linux | Insane | Signed JAR patching, SQLi, `ysoserial` and a symlink in `logs.tar` over SCP | [See](../machines/linux/fatty/README.md) | [EN](../machines/linux/fatty/README.en.md) |
| Feline | Linux | Hard | Tomcat CVE-2020-9484, SaltStack and `docker.sock` | [View](../machines/linux/feline/README.en.md) | [ES](../machines/linux/feline/README.md) |
| Fighter | Windows | Insane | SQLi with `xp_cmdshell`, AppLocker bypass via MSBuild and Capcom.sys | [ES](../machines/windows/fighter/README.md) | [Ver](../machines/windows/fighter/README.en.md) |
| Flight | Windows | Hard | LFI on `school.flight.htb`, Responder, SMB share and DCSync with Rubeus | [Ver](../machines/windows/flight/README.md) | [EN](../machines/windows/flight/README.en.md) |
| Fluffy | Windows | Easy | CVE-2025-24071, shadow credentials, ADCS ESC16 | [Ver](../machines/windows/fluffy/README.md) | [EN](../machines/windows/fluffy/README.en.md) |
| FluJab | Linux | Hard | Vhosts, SQLi, Ajenti, weak SSH keys and `screen` | [View](../machines/linux/flujab/README.en.md) | [ES](../machines/linux/flujab/README.md) |
| FluxCapacitor | Linux | Medium | WAF command injection and sudo over `.monit` | [View](../machines/linux/fluxcapacitor/README.en.md) | [ES](../machines/linux/fluxcapacitor/README.md) |
| Forest | Windows | Easy | AS-REP, `Account Operators` to Exchange, DCSync | [ES](../machines/windows/forest/README.md) | [Ver](../machines/windows/forest/README.en.md) |
| Forge | Linux | Medium | SSRF via redirect, internal FTP, SSH key and `pdb.post_mortem` | [Ver](../machines/linux/forge/README.md) | [EN](../machines/linux/forge/README.en.md) |
| Forgot | Linux | Medium | Host header reset, Varnish poisoning, ticket and pickle `.sav` | [Ver](../machines/linux/forgot/README.md) | [EN](../machines/linux/forgot/README.en.md) |
| Forgotten | Linux | Easy | LimeSurvey installer, malicious plugin and secret reuse | [Ver](../machines/linux/forgotten/README.md) | [EN](../machines/linux/forgotten/README.en.md) |
| Format | Linux | Medium | PHP microblog, Gitea, LFI/write, Redis socket and SSTI | [ES](../machines/linux/format/README.md) | [EN](../machines/linux/format/README.en.md) |
| FormulaX | Linux | Hard | Chat XSS, simple-git CVE-2022-25912, Mongo and LibreNMS | [View](../machines/linux/formulax/README.en.md) | [ES](../machines/linux/formulax/README.md) |
| Fortune | FreeBSD | Insane | Injection, client CA, `authpf` and NFS | [ES](../machines/freebsd/fortune/README.md) | [EN](../machines/freebsd/fortune/README.en.md) |
| ForwardSlash | Linux | Hard | LFI/XXE, backup binary, homemade cipher, LUKS and root key | [Ver](../machines/linux/forwardslash/README.md) | [EN](../machines/linux/forwardslash/README.en.md) |
| Freelancer | Windows | Hard | SQLi, `xp_cmdshell`, spray and RBCD | [View](../machines/windows/freelancer/README.en.md) | [ES](../machines/windows/freelancer/README.md) |
| FriendZone | Linux | Easy | AXFR, LFI + SMB, `os.py` hijack | [ES](../machines/linux/friendzone/README.md) | [Ver](../machines/linux/friendzone/README.en.md) |
| Fries | Windows | Hard | Gitea, pgAdmin CVE-2025-2945 and AD CS ESC | [View](../machines/windows/fries/README.en.md) | [ES](../machines/windows/fries/README.md) |
| Frolic | Linux | Easy | Client-side login, PlaySMS 1.4 CSV upload, SUID `rop` ret2libc | [Ver](../machines/linux/frolic/README.md) | [EN](../machines/linux/frolic/README.en.md) |
| Fulcrum | Linux | Insane | XXE, SSRF and AD pivot | [ES](../machines/linux/fulcrum/README.md) | [EN](../machines/linux/fulcrum/README.en.md) |
| Fuse | Windows | Medium | PaperCut, `cewl`/spray, RPC `svc-print`, WinRM and Capcom.sys | [ES](../machines/windows/fuse/README.md) | [Ver](../machines/windows/fuse/README.en.md) |
| Garfield | Windows | Hard | RODC, KeyList golden ticket, secretsdump, pass-the-hash | [Ver](../machines/windows/garfield/README.md) | [EN](../machines/windows/garfield/README.en.md) |
| Gavel | Linux | Medium | `.git`, PDO injection, PHP rules via runkit and `php.ini` | [ES](../machines/linux/gavel/README.md) | [Ver](../machines/linux/gavel/README.en.md) |
| Ghost | Windows | Insane | LDAP injection, Gitea, command injection, NetNTLMv2, gMSA, Golden SAML and trust | [ES](../machines/windows/ghost/README.md) | [Ver](../machines/windows/ghost/README.en.md) |
| Ghoul | Linux | Hard | ZipSlip, webshell, Gogs and SSH agent hijack | [Ver](../machines/linux/ghoul/README.md) | [EN](../machines/linux/ghoul/README.en.md) |
| Giddy | Windows | Medium | IIS SQLi, WinRM and UniFi Video as SYSTEM | [Ver](../machines/windows/giddy/README.md) | [EN](../machines/windows/giddy/README.en.md) |
| Giveback | Linux | Medium | GiveWP CVE-2024-5932, PHP-CGI CVE-2024-4577 and runc CVE-2024-21626 | [View](../machines/linux/giveback/README.en.md) | [ES](../machines/linux/giveback/README.md) |
| Gofer | Linux | Hard | SMB share, gopher SSRF to SMTP, ODT and a `notes` use-after-free | [ES](../machines/linux/gofer/README.md) | [Ver](../machines/linux/gofer/README.en.md) |
| Grandpa | Windows | Easy | IIS 6.0 CVE-2017-7269 and Churrasco escalation | [Ver](../machines/windows/grandpa/README.md) | [EN](../machines/windows/grandpa/README.en.md) |
| Granny | Windows | Easy | WebDAV `PUT`/`MOVE`, ASPX webshell and Churrasco | [Ver](../machines/windows/granny/README.md) | [EN](../machines/windows/granny/README.en.md) |
| GreenHorn | Linux | Easy | Pluck CMS, exposed Gitea and Depix | [ES](../machines/linux/greenhorn/README.md) | [Ver](../machines/linux/greenhorn/README.en.md) |
| Guardian | Linux | Hard | IDOR, PhpSpreadsheet XSS, LFI and a `safeapache2ctl` bypass | [View](../machines/linux/guardian/README.en.md) | [ES](../machines/linux/guardian/README.md) |
| Hackback | Windows | Insane | GoPhish, log poisoning, `reGeorg` to WinRM, named pipe and DiagHub | [See](../machines/windows/hackback/README.md) | [EN](../machines/windows/hackback/README.en.md) |
| HackNet | Linux | Medium | Django SSTI, pickle and GPG | [View](../machines/linux/hacknet/README.en.md) | [ES](../machines/linux/hacknet/README.md) |
| Haircut | Linux | Medium | `curl` option injection and `screen` CVE-2017-5618 | [ES](../machines/linux/haircut/README.md) | [Ver](../machines/linux/haircut/README.en.md) |
| Hancliffe | Windows | Hard | URI parsing, Nuxeo SSTI and buffer overflow with socket reuse | [ES](../machines/windows/hancliffe/README.md) | [Ver](../machines/windows/hancliffe/README.en.md) |
| Hawk | Linux | Medium | FTP, OpenSSL, Drupal and H2 `CREATE ALIAS` | [ES](../machines/linux/hawk/README.md) | [Ver](../machines/linux/hawk/README.en.md) |
| Haystack | Linux | Easy | Image clue, Elasticsearch, Kibana CVE-2018-17246 and Logstash as root | [ES](../machines/linux/haystack/README.md) | [Ver](../machines/linux/haystack/README.en.md) |
| Haze | Windows | Hard | Splunk CVE-2024-36991, gMSA and shadow credentials | [ES](../machines/windows/haze/README.md) | [Ver](../machines/windows/haze/README.en.md) |
| Headless | Linux | Easy | Header XSS, cookie theft, command injection and a relative-path `syscheck` | [See](../machines/linux/headless/README.md) | [EN](../machines/linux/headless/README.en.md) |
| Heal | Linux | Medium | Traversal, LimeSurvey and Consul | [ES](../machines/linux/heal/README.md) | [Ver](../machines/linux/heal/README.en.md) |
| Health | Linux | Medium | Redirect SSRF, Gogs SQLi and root cron | [View](../machines/linux/health/README.en.md) | [ES](../machines/linux/health/README.md) |
| Heist | Windows | Easy | Cisco config with type 7 and type 5, WinRM spray and `procdump` on Firefox | [ES](../machines/windows/heist/README.md) | [Ver](../machines/windows/heist/README.en.md) |
| Helix | Linux | Medium | NiFi + H2 `CREATE ALIAS`, OPC UA | [ES](../machines/linux/helix/README.md) | [Ver](../machines/linux/helix/README.en.md) |
| Helpline | Windows | Hard | ServiceDesk XXE/LFI, WinRM and EFS | [ES](../machines/windows/helpline/README.md) | [Ver](../machines/windows/helpline/README.en.md) |
| Holiday | Linux | Hard | SQLi, XSS, command injection and `npm` | [View](../machines/linux/holiday/README.en.md) | [ES](../machines/linux/holiday/README.md) |
| Horizontall | Linux | Easy | Strapi CVE-2019-19609 and Laravel Ignition CVE-2021-3129 over a tunnel | [Ver](../machines/linux/horizontall/README.md) | [EN](../machines/linux/horizontall/README.en.md) |
| Hospital | Windows | Medium | `.phar`, CVE-2023-35001, Ghostscript and XAMPP | [ES](../machines/windows/hospital/README.md) | [Ver](../machines/windows/hospital/README.en.md) |
| IClean | Linux | Medium | XSS, Jinja SSTI, SHA-256 cracking and `qpdf` under sudo | [ES](../machines/linux/iclean/README.md) | [Ver](../machines/linux/iclean/README.en.md) |
| Imagery | Linux | Medium | Stored XSS, traversal, command injection, pyAesCrypt backup and `charcol` | [ES](../machines/linux/imagery/README.md) | [Ver](../machines/linux/imagery/README.en.md) |
| Inception | Linux | Medium | dompdf CVE-2014-2383, WebDAV, forward shell and `apt` pre-invoke over TFTP | [See](../machines/linux/inception/README.md) | [EN](../machines/linux/inception/README.en.md) |
| Intelligence | Windows | Medium | PDF metadata, password spray, `web*` DNS, Responder, GMSA and RBCD | [Ver](../machines/windows/intelligence/README.md) | [EN](../machines/windows/intelligence/README.en.md) |
| Intense | Linux | Hard | SQLi, hash extension, SNMP RW and canary ROP | [ES](../machines/linux/intense/README.md) | [Ver](../machines/linux/intense/README.en.md) |
| Intentions | Linux | Hard | Second-order SQLi, Imagick and `CAP_DAC_READ_SEARCH` | [ES](../machines/linux/intentions/README.md) | [EN](../machines/linux/intentions/README.en.md) |
| Interpreter | Linux | Medium | Mirth CVE-2023-43208, PBKDF2, `eval()` | [ES](../machines/linux/interpreter/README.md) | [Ver](../machines/linux/interpreter/README.en.md) |
| Intuition | Linux | Hard | XSS, file read, Suricata logs and `ansible-galaxy` | [ES](../machines/linux/intuition/README.md) | [Ver](../machines/linux/intuition/README.en.md) |
| Investigation | Linux | Medium | ExifTool CVE-2022-23935, EVTX and sudo Perl binary | [ES](../machines/linux/investigation/README.md) | [EN](../machines/linux/investigation/README.en.md) |
| Irked | Linux | Easy | UnrealIRCd 3.2.8.1, `AB;`, steghide, SSH and a SUID `viewuser` | [ES](../machines/linux/irked/README.md) | [Ver](../machines/linux/irked/README.en.md) |
| Jab | Windows | Medium | Openfire CVE-2023-32315, plugin RCE, XMPP and DCOM MMC20 | [Ver](../machines/windows/jab/README.md) | [EN](../machines/windows/jab/README.en.md) |
| Jail | Linux | Insane | BOF, NFS without squash, `rvim` and RSA | [ES](../machines/linux/jail/README.md) | [EN](../machines/linux/jail/README.en.md) |
| Jarvis | Linux | Medium | SQLi, phpMyAdmin CVE-2018-12613 and SUID `systemctl` | [Ver](../machines/linux/jarvis/README.md) | [EN](../machines/linux/jarvis/README.en.md) |
| Jeeves | Windows | Medium | Unauthenticated Jenkins, KeePass, pass-the-hash and a flag in an NTFS stream | [ES](../machines/windows/jeeves/README.md) | [Ver](../machines/windows/jeeves/README.en.md) |
| Jerry | Windows | Easy | Tomcat 7 with default credentials, WAR via `/manager/text` and a direct SYSTEM shell | [ES](../machines/windows/jerry/README.md) | [Ver](../machines/windows/jerry/README.en.md) |
| Jewel | Linux | Medium | GitWeb, Rails Redis deserialization; TOTP and `sudo gem` | [ES](../machines/linux/jewel/README.md) | [EN](../machines/linux/jewel/README.en.md) |
| Joker | Linux | Hard | TFTP/Squid, Werkzeug, sudoedit and `tar` wildcard | [ES](../machines/linux/joker/README.md) | [Ver](../machines/linux/joker/README.en.md) |
| Json | Windows | Medium | Json.Net Bearer with ysoserial, FileZilla and JuicyPotato | [ES](../machines/windows/json/README.md) | [Ver](../machines/windows/json/README.en.md) |
| Jupiter | Linux | Medium | Grafana/PostgreSQL COPY PROGRAM, Jupyter and sattrack | [View](../machines/linux/jupiter/README.md) | [EN](../machines/linux/jupiter/README.en.md) |
| Keeper | Linux | Easy | Default Request Tracker, ticket credentials and KeePass CVE-2023-32784 | [Ver](../machines/linux/keeper/README.md) | [EN](../machines/linux/keeper/README.en.md) |
| Knife | Linux | Easy | PHP 8.1.0-dev backdoor and `sudo knife` | [ES](../machines/linux/knife/README.md) | [EN](../machines/linux/knife/README.en.md) |
| Kobold | Linux | Easy | MCPJam CVE-2026-23744, PrivateBin, Docker | [ES](../machines/linux/kobold/README.md) | [Ver](../machines/linux/kobold/README.en.md) |
| Kotarak | Linux | Hard | Ghostcat, SSRF, `ntds.dit` and Wget CVE-2016-4971 | [ES](../machines/linux/kotarak/README.md) | [Ver](../machines/linux/kotarak/README.en.md) |
| Laboratory | Linux | Easy | GitLab CVE-2020-10977 and SUID PATH hijacking | [View](../machines/linux/laboratory/README.md) | [EN](../machines/linux/laboratory/README.en.md) |
| LaCasaDePapel | Linux | Easy | Backdoored vsftpd, client certificate and Supervisor | [View](../machines/linux/lacasadepapel/README.en.md) | [ES](../machines/linux/lacasadepapel/README.md) |
| Lame | Linux | Easy | Samba `usermap_script` (CVE-2007-2447) for direct root; `distcc` and `vsftpd` as alternates | [ES](../machines/linux/lame/README.md) | [Ver](../machines/linux/lame/README.en.md) |
| Lantern | Linux | Hard | Skipper CVE-2022-38580 SSRF, SQLite, arbitrary write and Razor DLL | [ES](../machines/linux/lantern/README.md) | [Ver](../machines/linux/lantern/README.en.md) |
| Laser | Linux | Insane | PRET/PJL, gRPC, Solr and `sshpass` MITM | [ES](../machines/linux/laser/README.md) | [EN](../machines/linux/laser/README.en.md) |
| Late | Linux | Easy | OCR SSTI and writable login script | [View](../machines/linux/late/README.en.md) | [ES](../machines/linux/late/README.md) |
| Lazy | Linux | Medium | Cookie padding oracle and SUID `backup` PATH hijacking | [View](../machines/linux/lazy/README.en.md) | [ES](../machines/linux/lazy/README.md) |
| Legacy | Windows | Easy | MS08-067 over SMBv1 on Windows XP | [ES](../machines/windows/legacy/README.md) | [Ver](../machines/windows/legacy/README.en.md) |
| Lightweight | Linux | Medium | Cleartext LDAP, backup and OpenSSL capabilities | [View](../machines/linux/lightweight/README.en.md) | [ES](../machines/linux/lightweight/README.md) |
| LinkVortex | Linux | Easy | `.git`, Ghost CVE-2023-40028 and TOCTOU | [ES](../machines/linux/linkvortex/README.md) | [Ver](../machines/linux/linkvortex/README.en.md) |
| Love | Windows | Easy | SSRF, PHP upload and AlwaysInstallElevated | [ES](../machines/windows/love/README.md) | [EN](../machines/windows/love/README.en.md) |
| Luanne | NetBSD | Easy | Supervisor, Lua, `doas` and PGP | [ES](../machines/netbsd/luanne/README.md) | [EN](../machines/netbsd/luanne/README.en.md) |
| Luke | FreeBSD | Medium | Cleartext `config.php`, an API with JWT and Ajenti as root | [Ver](../machines/freebsd/luke/README.md) | [EN](../machines/freebsd/luke/README.en.md) |
| Magic | Linux | Medium | SQLi, `.php.jpg` upload, SUID and PATH hijack | [View](../machines/linux/magic/README.en.md) | [ES](../machines/linux/magic/README.md) |
| MagicGardens | Linux | Insane | QR XSS, IPv6 overflow, Docker and CAP_SYS_MODULE | [View](../machines/linux/magicgardens/README.md) | [EN](../machines/linux/magicgardens/README.en.md) |
| Mailing | Windows | Easy | LFI to hMailServer, MonikerLink and macro | [Ver](../machines/windows/mailing/README.md) | [EN](../machines/windows/mailing/README.en.md) |
| Mailroom | Linux | Hard | XSS, NoSQL, command injection and `strace` on `kpcli` | [See](../machines/linux/mailroom/README.md) | [EN](../machines/linux/mailroom/README.en.md) |
| MakeSense | Linux | Medium | Season 11: admin-bot XSS, forged AES-GCM, malicious plugin and OCR as root | [Ver](../machines/linux/makesense/README.md) | [EN](../machines/linux/makesense/README.en.md) |
| Manager | Windows | Medium | User:password spray, `xp_dirtree`, AD CS ESC7 and WinRM | [View](../machines/windows/manager/README.en.md) | [ES](../machines/windows/manager/README.md) |
| Mango | Linux | Medium | NoSQL `$ne`/`$regex`, SSH and SUID `jjs` | [Ver](../machines/linux/mango/README.md) | [EN](../machines/linux/mango/README.en.md) |
| Mantis | Windows | Hard | Orchard CMS, MSSQL and MS14-068 (forged PAC) | [Ver](../machines/windows/mantis/README.md) | [EN](../machines/windows/mantis/README.en.md) |
| Mentor | Linux | Medium | SNMP, API JWT, container, uvicorn and `sudo /bin/sh` | [Ver](../machines/linux/mentor/README.md) | [EN](../machines/linux/mentor/README.en.md) |
| Meta | Linux | Medium | ExifTool CVE-2021-22204 and editable cron | [Ver](../machines/linux/meta/README.md) | [EN](../machines/linux/meta/README.en.md) |
| MetaTwo | Linux | Easy | BookingPress SQLi, XXE, FTP and Passpie | [View](../machines/linux/metatwo/README.en.md) | [ES](../machines/linux/metatwo/README.md) |
| Minion | Windows | Insane | SSRF, ICMP C2, scheduled task and ADS | [ES](../machines/windows/minion/README.md) | [EN](../machines/windows/minion/README.en.md) |
| Mirage | Windows | Hard | NATS, Kerberoast, relay, GMSA and ESC10 | [ES](../machines/windows/mirage/README.md) | [Ver](../machines/windows/mirage/README.en.md) |
| Mirai | Linux | Easy | Pi-hole/Plex, default credentials, `sudo ALL` and a deleted flag recovered from USB | [ES](../machines/linux/mirai/README.md) | [Ver](../machines/linux/mirai/README.en.md) |
| Mischief | Linux | Insane | SNMP/IPv6, command injection and `systemd-run` | [View](../machines/linux/mischief/README.en.md) | [ES](../machines/linux/mischief/README.md) |
| Mist | Windows | Insane | Pluck CMS, PetitPotam, shadow credentials, ESC13 and Backup Operators | [ES](../machines/windows/mist/README.md) | [EN](../machines/windows/mist/README.en.md) |
| Monitored | Linux | Medium | SNMP credentials, Nagios CVE-2023-40931 and binary replacement | [ES](../machines/linux/monitored/README.md) | [Ver](../machines/linux/monitored/README.en.md) |
| MonitorsFour | Windows | Easy | IDOR en la API, MD5 crackeado, CVE-2025-24367 en Cacti, escape por la API de Docker | [ES](../machines/windows/monitorsfour/README.md) | [Ver](../machines/windows/monitorsfour/README.en.md) |
| MonitorsThree | Linux | Medium | Reset SQLi, Cacti CVE-2024-25642 and Duplicati | [View](../machines/linux/monitorsthree/README.en.md) | [ES](../machines/linux/monitorsthree/README.md) |
| MonitorsTwo | Linux | Easy | Cacti CVE-2022-46169 and Docker escape CVE-2021-41091 | [ES](../machines/linux/monitorstwo/README.md) | [EN](../machines/linux/monitorstwo/README.en.md) |
| Monteverde | Windows | Medium | Anonymous LDAP, `azure.xml` and Azure AD Connect credentials | [Ver](../machines/windows/monteverde/README.md) | [EN](../machines/windows/monteverde/README.en.md) |
| Multimaster | Windows | Insane | SQLi, CEF debug, GenericWrite/AS-REP and Server Operators | [ES](../machines/windows/multimaster/README.md) | [Ver](../machines/windows/multimaster/README.en.md) |
| NanoCorp | Windows | Hard | `.library-ms`/NetNTLMv2, AD ACLs and Checkmk CVE-2024-0670 | [ES](../machines/windows/nanocorp/README.md) | [Ver](../machines/windows/nanocorp/README.en.md) |
| Napper | Windows | Hard | Blog credentials, NAPLISTENER, Elastic LAPS and `RunasCs --bypass-uac` | [ES](../machines/windows/napper/README.md) | [Ver](../machines/windows/napper/README.en.md) |
| Nest | Windows | Easy | Guest SMB, `RU_config.xml`, VB decryption, `c.smith`, ADS and `psexec` | [ES](../machines/windows/nest/README.md) | [Ver](../machines/windows/nest/README.en.md) |
| Netmon | Windows | Easy | Anonymous FTP, PRTG and CVE-2018-9276 | [ES](../machines/windows/netmon/README.md) | [Ver](../machines/windows/netmon/README.en.md) |
| Networked | Linux | Easy | Source-code backup, double extension, injectable cron and unquoted `sudo` | [ES](../machines/linux/networked/README.md) | [Ver](../machines/linux/networked/README.en.md) |
| Nibbles | Linux | Easy | Nibbleblog 4.0.3, subida CVE-2015-6967, sudo | [ES](../machines/linux/nibbles/README.md) | [Ver](../machines/linux/nibbles/README.en.md) |
| Nineveh | Linux | Medium | phpLiteAdmin + LFI, port knocking and chkrootkit 0.49 as root | [ES](../machines/linux/nineveh/README.md) | [Ver](../machines/linux/nineveh/README.en.md) |
| Nocturnal | Linux | Easy | IDOR, backup command injection, SQLite MD5 and ISPConfig CVE-2023-46818 | [Ver](../machines/linux/nocturnal/README.md) | [EN](../machines/linux/nocturnal/README.en.md) |
| Node | Linux | Medium | `/api/users/latest` leaking hashes, backup ZIP, SSH `mark`, MongoDB tasks and a SUID `backup` BOF | [ES](../machines/linux/node/README.md) | [Ver](../machines/linux/node/README.en.md) |
| Obscurity | Linux | Medium | Python server, homemade cipher and BetterSSH | [View](../machines/linux/obscurity/README.en.md) | [ES](../machines/linux/obscurity/README.md) |
| October | Linux | Medium | October CMS, `.php5` upload and ret2libc with 9-bit ASLR | [ES](../machines/linux/october/README.md) | [EN](../machines/linux/october/README.en.md) |
| Office | Windows | Hard | Joomla CVE-2023-23752, Kerberos PCAP, LibreOffice CVE-2023-2255, DPAPI and GPO | [See](../machines/windows/office/README.md) | [EN](../machines/windows/office/README.en.md) |
| Olympus | Linux | Medium | Xdebug, aircrack-ng, port knocking and the `docker` group | [ES](../machines/linux/olympus/README.md) | [Ver](../machines/linux/olympus/README.en.md) |
| Omni | Windows | Easy | Windows IoT Core, SirepRAT, `reg save`, WDP and `Import-Clixml` | [ES](../machines/windows/omni/README.md) | [Ver](../machines/windows/omni/README.en.md) |
| OneTwoSeven | Linux | Hard | SFTP symlinks, plugin bypass and apt poisoning | [ES](../machines/linux/onetwoseven/README.md) | [EN](../machines/linux/onetwoseven/README.en.md) |
| OnlyForYou | Linux | Medium | Absolute LFI, `dig` command injection, Cypher and root `pip` | [ES](../machines/linux/onlyforyou/README.md) | [EN](../machines/linux/onlyforyou/README.en.md) |
| Oouch | Linux | Hard | OAuth CSRF, uWSGI and D-Bus | [View](../machines/linux/oouch/README.md) | [EN](../machines/linux/oouch/README.en.md) |
| OpenAdmin | Linux | Easy | OpenNetAdmin 18.1.1, credential reuse, `ssh2john` and a `nano` escape | [ES](../machines/linux/openadmin/README.md) | [Ver](../machines/linux/openadmin/README.en.md) |
| OpenKeyS | OpenBSD | Medium | CVE-2019-19521, `xlock` and S/Key | [ES](../machines/openbsd/openkeys/README.md) | [EN](../machines/openbsd/openkeys/README.en.md) |
| OpenSource | Linux | Easy | Flask path traversal, Gitea/chisel, dev01 key and root git hook | [Ver](../machines/linux/opensource/README.md) | [EN](../machines/linux/opensource/README.en.md) |
| Ophiuchi | Linux | Medium | SnakeYAML, Tomcat and `go run` with Wasm | [ES](../machines/linux/ophiuchi/README.md) | [Ver](../machines/linux/ophiuchi/README.en.md) |
| Optimum | Windows | Easy | Rejetto HFS 2.3 (CVE-2014-6287) and MS16-032 up to SYSTEM | [ES](../machines/windows/optimum/README.md) | [Ver](../machines/windows/optimum/README.en.md) |
| Ouija | Linux | Insane | Request smuggling, hash length extension and PHP extension | [View](../machines/linux/ouija/README.en.md) | [ES](../machines/linux/ouija/README.md) |
| Outbound | Linux | Easy | Roundcube CVE-2025-49113, decrypted sessions and a `below` symlink | [ES](../machines/linux/outbound/README.md) | [Ver](../machines/linux/outbound/README.en.md) |
| Outdated | Windows | Medium | Follina CVE-2022-30190, shadow credentials and WSUS abuse | [Ver](../machines/windows/outdated/README.md) | [EN](../machines/windows/outdated/README.en.md) |
| Overflow | Linux | Hard | Padding oracle, SQLi, ExifTool CVE-2021-22204 and TOCTOU | [View](../machines/linux/overflow/README.en.md) | [ES](../machines/linux/overflow/README.md) |
| Overwatch | Windows | Medium | Anonymous SMB, MSSQL, ADIDNS and WCF | [View](../machines/windows/overwatch/README.en.md) | [ES](../machines/windows/overwatch/README.md) |
| Oz | Linux | Hard | SQLi, SSTI, port knocking and Portainer | [View](../machines/linux/oz/README.en.md) | [ES](../machines/linux/oz/README.md) |
| Pandora | Linux | Medium | SNMP, Pandora FMS SQLi and SUID PATH hijack | [Ver](../machines/linux/pandora/README.md) | [EN](../machines/linux/pandora/README.en.md) |
| Paper | Linux | Medium | WordPress draft, Rocket.Chat CVE-2019-17671 and polkit | [Ver](../machines/linux/paper/README.md) | [EN](../machines/linux/paper/README.en.md) |
| Passage | Linux | Medium | CuteNews, flat-file hashes and USBCreator | [ES](../machines/linux/passage/README.md) | [Ver](../machines/linux/passage/README.en.md) |
| Patents | Linux | Hard | LibreOffice XXE, log poisoning and binary service | [View](../machines/linux/patents/README.en.md) | [ES](../machines/linux/patents/README.md) |
| PC | Linux | Easy | gRPC reflection, SQLite SQLi and pyLoad CVE-2023-0297 | [View](../machines/linux/pc/README.en.md) | [ES](../machines/linux/pc/README.md) |
| Perfection | Linux | Easy | ERB SSTI, newline bypass and Hashcat mask | [View](../machines/linux/perfection/README.en.md) | [ES](../machines/linux/perfection/README.md) |
| PermX | Linux | Easy | Chamilo CVE-2023-4220, credentials and `setfacl` symlink | [ES](../machines/linux/permx/README.md) | [Ver](../machines/linux/permx/README.en.md) |
| Perspective | Windows | Insane | SHTML, machineKey/ViewState and padding oracle | [View](../machines/windows/perspective/README.md) | [EN](../machines/windows/perspective/README.en.md) |
| Phoenix | Linux | Hard | WordPress/Asgaros SQLi, TOTP, PAM and `rsync` wildcard | [Ver](../machines/linux/phoenix/README.md) | [EN](../machines/linux/phoenix/README.en.md) |
| Photobomb | Linux | Easy | Credentials in JavaScript, `filetype` injection and PATH hijack | [Ver](../machines/linux/photobomb/README.md) | [EN](../machines/linux/photobomb/README.en.md) |
| Pikaboo | Linux | Hard | nginx off-by-slash, LDAP, FTP log poisoning LFI and Perl `open` | [Ver](../machines/linux/pikaboo/README.md) | [EN](../machines/linux/pikaboo/README.en.md) |
| PikaTwoo | Linux | Insane | SQLi, APISIX, Kubernetes and cr8escape | [ES](../machines/linux/pikatwoo/README.md) | [EN](../machines/linux/pikatwoo/README.en.md) |
| Pilgrimage | Linux | Easy | `/.git`, ImageMagick CVE-2022-44268 and binwalk CVE-2022-4510 | [Ver](../machines/linux/pilgrimage/README.md) | [EN](../machines/linux/pilgrimage/README.en.md) |
| PingPong | Windows | Insane | Dual AD forest, ESC13, pivot, gMSA, JEA, RBCD and ESC4→ESC1 | [ES](../machines/windows/pingpong/README.md) | [Ver](../machines/windows/pingpong/README.en.md) |
| Pirate | Windows | Hard | Pre-Windows 2000, gMSA, RBCD, S4U2Proxy | [ES](../machines/windows/pirate/README.md) | [Ver](../machines/windows/pirate/README.en.md) |
| Pit | Linux | Medium | SNMP, SeedDMS CVE-2019-12744 and monitoring scripts as root | [ES](../machines/linux/pit/README.md) | [Ver](../machines/linux/pit/README.en.md) |
| PivotAPI | Windows | Insane | FTP/metadata, AS-REP, reversing, MSSQL and LAPS | [View](../machines/windows/pivotapi/README.en.md) | [ES](../machines/windows/pivotapi/README.md) |
| Planning | Linux | Easy | Grafana CVE-2024-9264, credentials and Crontab UI | [ES](../machines/linux/planning/README.md) | [Ver](../machines/linux/planning/README.en.md) |
| Player | Linux | Hard | Leaked JWT key, ffmpeg AVI, lshell and a Codiad cron | [ES](../machines/linux/player/README.md) | [Ver](../machines/linux/player/README.en.md) |
| Poison | FreeBSD | Medium | LFI in `browse.php`, base64 in `pwdbackup.txt`, VNC as root with `secret.zip` | [Ver](../machines/freebsd/poison/README.md) | [EN](../machines/freebsd/poison/README.en.md) |
| Pollution | Linux | Hard | XXE, Redis sessions, filter injection and prototype pollution | [View](../machines/linux/pollution/README.en.md) | [ES](../machines/linux/pollution/README.md) |
| Popcorn | Linux | Medium | Upload filter bypass, PHP webshell, PAM CVE-2010-0832 and Dirty COW | [ES](../machines/linux/popcorn/README.md) | [Ver](../machines/linux/popcorn/README.en.md) |
| Postman | Linux | Easy | Unauthenticated Redis, SSH cracking and Webmin CVE-2019-12840 | [ES](../machines/linux/postman/README.md) | [Ver](../machines/linux/postman/README.en.md) |
| Pov | Windows | Medium | `machineKey` file read, ViewState and `SeDebugPrivilege` | [ES](../machines/windows/pov/README.md) | [Ver](../machines/windows/pov/README.en.md) |
| Precious | Linux | Easy | PDFKit SSRF, file read and YAML with `sudo` | [View](../machines/linux/precious/README.en.md) | [ES](../machines/linux/precious/README.md) |
| Previous | Linux | Medium | Next.js CVE-2025-29927, traversal, NextAuth and Terraform through `sudo` | [See](../machines/linux/previous/README.md) | [EN](../machines/linux/previous/README.en.md) |
| Previse | Linux | Easy | Execute-after-redirect, injection and path hijack | [ES](../machines/linux/previse/README.md) | [Ver](../machines/linux/previse/README.en.md) |
| Pterodactyl | Linux | Medium | CVE-2025-49132 en `/locales`, PEAR `pearcmd`, cadena CVE-2025-6018/6019 | [ES](../machines/linux/pterodactyl/README.md) | [Ver](../machines/linux/pterodactyl/README.en.md) |
| Puppy | Windows | Medium | AD, GenericWrite, KeePassXC, DPAPI and GenericAll | [ES](../machines/windows/puppy/README.md) | [Ver](../machines/windows/puppy/README.en.md) |
| Querier | Windows | Medium | Credentials in a macro, `xp_dirtree`, NetNTLMv2 and GPP | [Ver](../machines/windows/querier/README.md) | [EN](../machines/windows/querier/README.en.md) |
| Quick | Linux | Hard | QUIC/HTTP3, ESI and a file race | [View](../machines/linux/quick/README.en.md) | [ES](../machines/linux/quick/README.md) |
| Rabbit | Windows | Insane | SQLi, OWA, macro phishing and SYSTEM webshell | [View](../machines/windows/rabbit/README.en.md) | [ES](../machines/windows/rabbit/README.md) |
| Rainbow | Windows | Medium | Anonymous FTP, service restart and `fodhelper` UAC bypass | [Ver](../machines/windows/rainbow/README.md) | [EN](../machines/windows/rainbow/README.en.md) |
| RainyDay | Linux | Hard | IDOR, containers, `cwd` escape and Unicode truncation | [ES](../machines/linux/rainyday/README.md) | [Ver](../machines/linux/rainyday/README.en.md) |
| Reactor | Linux | Easy | React2Shell and Node inspector | [ES](../machines/linux/reactor/README.md) | [Ver](../machines/linux/reactor/README.en.md) |
| Rebound | Windows | Insane | AD, Kerberoasting, shadow credentials, GMSA and RBCD | [View](../machines/windows/rebound/README.en.md) | [ES](../machines/windows/rebound/README.md) |
| RedCross | Linux | Medium | XSS/cookie, Haraka, PostgreSQL/NSS and `iptctl` BOF | [ES](../machines/linux/redcross/README.md) | [EN](../machines/linux/redcross/README.en.md) |
| Reddish | Linux | Insane | Node-RED, Docker pivot, Redis and privileged container | [ES](../machines/linux/reddish/README.md) | [EN](../machines/linux/reddish/README.en.md) |
| RedPanda | Linux | Easy | Thymeleaf SSTI, JPEG metadata and XXE as root | [ES](../machines/linux/redpanda/README.md) | [Ver](../machines/linux/redpanda/README.en.md) |
| Reel | Windows | Hard | RTF CVE-2017-0199, WriteOwner/WriteDacl ACLs and backup script | [ES](../machines/windows/reel/README.md) | [Ver](../machines/windows/reel/README.en.md) |
| Reel2 | Windows | Hard | OWA spray, Responder, JEA bypass and StickyNotes | [ES](../machines/windows/reel2/README.md) | [EN](../machines/windows/reel2/README.en.md) |
| Registry | Linux | Hard | Docker registry, Bolt CMS and `restic` as root | [ES](../machines/linux/registry/README.md) | [Ver](../machines/linux/registry/README.en.md) |
| Remote | Windows | Medium | NFS with the Umbraco backup, SHA1, XSLT RCE and TeamViewer | [Ver](../machines/windows/remote/README.md) | [EN](../machines/windows/remote/README.en.md) |
| Resolute | Windows | Medium | Anonymous LDAP, password reuse and `DnsAdmins` | [ES](../machines/windows/resolute/README.md) | [Ver](../machines/windows/resolute/README.en.md) |
| Resource | Linux | Hard | PHAR, SSH CA and Bash glob | [ES](../machines/linux/resource/README.md) | [Ver](../machines/linux/resource/README.en.md) |
| Response | Linux | Insane | HMAC SSRF, rogue LDAP, TLS traversal and PCAP forensics | [View](../machines/linux/response/README.en.md) | [ES](../machines/linux/response/README.md) |
| Retired | Linux | Medium | File read, ROP, backup symlink and `binfmt_misc` | [Ver](../machines/linux/retired/README.md) | [EN](../machines/linux/retired/README.en.md) |
| RetroTwo | Windows | Easy | Access macro, Pre-Windows 2000 computer accounts and ZeroLogon | [Ver](../machines/windows/retrotwo/README.md) | [EN](../machines/windows/retrotwo/README.en.md) |
| Return | Windows | Easy | Printer panel, LDAP bind, WinRM and `Server Operators` | [Ver](../machines/windows/return/README.md) | [EN](../machines/windows/return/README.en.md) |
| Rope | Linux | Insane | Remote format string, GOT overwrite and ROP with canary/PIE | [Ver](../machines/linux/rope/README.md) | [EN](../machines/linux/rope/README.en.md) |
| Runner | Linux | Medium | TeamCity CVE-2023-42793, Portainer and runc CVE-2024-21626 | [View](../machines/linux/runner/README.md) | [EN](../machines/linux/runner/README.en.md) |
| RustyKey | Windows | Hard | Timeroasting, 7-Zip extension and RBCD | [View](../machines/windows/rustykey/README.md) | [EN](../machines/windows/rustykey/README.en.md) |
| Safe | Linux | Easy | x86-64 buffer overflow/ROP, libc leak, KeePass and root password reuse | [ES](../machines/linux/safe/README.md) | [Ver](../machines/linux/safe/README.en.md) |
| Sandworm | Linux | Medium | SSTI, Firejail, Rust crate and CVE-2022-31214 | [Ver](../machines/linux/sandworm/README.md) | [EN](../machines/linux/sandworm/README.en.md) |
| Sau | Linux | Easy | Request Baskets SSRF into Maltrail, then `sudo systemctl` pager escape | [ES](../machines/linux/sau/README.md) | [Ver](../machines/linux/sau/README.en.md) |
| Sauna | Windows | Easy | AS-REP roasting, autologon credentials and DCSync | [ES](../machines/windows/sauna/README.md) | [Ver](../machines/windows/sauna/README.en.md) |
| Scavenger | Linux | Hard | Whois SQLi, PrestaShop, rootkit and Exim CVE-2019-10149 | [ES](../machines/linux/scavenger/README.md) | [Ver](../machines/linux/scavenger/README.en.md) |
| Scepter | Windows | Hard | NFS with PFX, ADCS ESC14 and DCSync | [View](../machines/windows/scepter/README.en.md) | [ES](../machines/windows/scepter/README.md) |
| Schooled | FreeBSD | Medium | Moodle, XSS/CVE-2020-25627, plugin and `pkg` package | [ES](../machines/freebsd/schooled/README.md) | [EN](../machines/freebsd/schooled/README.en.md) |
| Scrambled | Windows | Medium | Kerberoast `sqlsvc`, silver ticket and `BinaryFormatter` in `ScrambleClient.exe` | [Ver](../machines/windows/scrambled/README.md) | [EN](../machines/windows/scrambled/README.en.md) |
| ScriptKiddie | Linux | Easy | `msfvenom` CVE-2020-7384, `incron` and `sudo msfconsole` | [See](../machines/linux/scriptkiddie/README.md) | [EN](../machines/linux/scriptkiddie/README.en.md) |
| Sea | Linux | Easy | WonderCMS CVE-2023-41425, cracked hash, command injection on 8080 | [Ver](../machines/linux/sea/README.md) | [EN](../machines/linux/sea/README.en.md) |
| Seal | Linux | Medium | GitBucket, Nginx/Tomcat differential and Ansible | [View](../machines/linux/seal/README.en.md) | [ES](../machines/linux/seal/README.md) |
| Search | Windows | Hard | Image credentials, WDigest, gMSA and NTDS | [Ver](../machines/windows/search/README.md) | [EN](../machines/windows/search/README.en.md) |
| SecNotes | Windows | Medium | CSRF to admin, SMB webshell and WSL `bash.exe` | [Ver](../machines/windows/secnotes/README.md) | [EN](../machines/windows/secnotes/README.en.md) |
| Sekhmet | Windows | Insane | Node.js deserialization, `bkcrack`, LDAP injection and DPAPI | [Ver](../machines/windows/sekhmet/README.md) | [EN](../machines/windows/sekhmet/README.en.md) |
| Sense | FreeBSD | Easy | pfSense 2.1.3 with default credentials and CVE-2014-4688 as root | [ES](../machines/freebsd/sense/README.md) | [Ver](../machines/freebsd/sense/README.en.md) |
| Servmon | Windows | Easy | NVMS path traversal, NSClient++ and SSH tunnel | [ES](../machines/windows/servmon/README.md) | [Ver](../machines/windows/servmon/README.en.md) |
| Seventeen | Linux | Hard | Boolean SQLi, SFMS, Roundcube CVE-2020-12640 and malicious npm module in Verdaccio | [ES](../machines/linux/seventeen/README.md) | [Ver](../machines/linux/seventeen/README.en.md) |
| Shared | Linux | Medium | Cookie SQLi, IPython CVE-2022-21699 and Redis Lua | [View](../machines/linux/shared/README.en.md) | [ES](../machines/linux/shared/README.md) |
| Sharp | Windows | Hard | PortableKanban, .NET Remoting and WCF | [View](../machines/windows/sharp/README.en.md) | [ES](../machines/windows/sharp/README.md) |
| Shibboleth | Linux | Medium | IPMI RAKP, Zabbix and MariaDB UDF | [View](../machines/linux/shibboleth/README.en.md) | [ES](../machines/linux/shibboleth/README.md) |
| Shocker | Linux | Easy | Shellshock in a CGI (`user.sh`) and `sudo perl` via GTFOBins | [ES](../machines/linux/shocker/README.md) | [Ver](../machines/linux/shocker/README.en.md) |
| Shrek | Linux | Hard | MP3 steganography, FTP, encrypted SSH key and a `chown` wildcard | [See](../machines/linux/shrek/README.md) | [EN](../machines/linux/shrek/README.en.md) |
| Sightless | Linux | Easy | SQLPad CVE-2022-0944, Froxlor and WebDriver | [ES](../machines/linux/sightless/README.md) | [Ver](../machines/linux/sightless/README.en.md) |
| Signed | Windows | Medium | MSSQL, silver ticket and `OPENROWSET` | [ES](../machines/windows/signed/README.md) | [Ver](../machines/windows/signed/README.en.md) |
| Silentium | Linux | Easy | Flowise reset token, CVE-2025-59528, Docker and Gogs CVE-2025-8110 | [ES](../machines/linux/silentium/README.md) | [EN](../machines/linux/silentium/README.en.md) |
| Silo | Windows | Medium | Oracle 11g XE, ODAT and SYSTEM execution | [ES](../machines/windows/silo/README.md) | [EN](../machines/windows/silo/README.en.md) |
| Sink | Linux | Insane | Smuggling, Gitea, AWS KMS | [ES](../machines/linux/sink/README.md) | [Ver](../machines/linux/sink/README.en.md) |
| Sizzle | Windows | Insane | SCF/Responder, ADCS, Kerberoasting and DCSync | [ES](../machines/windows/sizzle/README.md) | [Ver](../machines/windows/sizzle/README.en.md) |
| Skyfall | Linux | Insane | MinIO CVE-2023-28432, Vault, FUSE memfs and master token | [Ver](../machines/linux/skyfall/README.md) | [EN](../machines/linux/skyfall/README.en.md) |
| Smasher2 | Linux | Insane | Source in `/backup`, `ses.so` bug and credential `mmap` | [ES](../machines/linux/smasher2/README.md) | [Ver](../machines/linux/smasher2/README.en.md) |
| Sneaky | Linux | Medium | SNMP, IPv6, login SQLi and SUID overflow | [ES](../machines/linux/sneaky/README.md) | [EN](../machines/linux/sneaky/README.en.md) |
| SneakyMailer | Linux | Medium | SMTP, phishing, IMAP, FTP and PyPI package | [View](../machines/linux/sneakymailer/README.en.md) | [ES](../machines/linux/sneakymailer/README.md) |
| Sniper | Windows | Medium | LFI/RFI, SMB and `runas /savecred` | [Ver](../machines/windows/sniper/README.md) | [EN](../machines/windows/sniper/README.en.md) |
| Soccer | Linux | Easy | Default Tiny File Manager, blind WebSocket SQLi and `doas` with `dstat` | [ES](../machines/linux/soccer/README.md) | [Ver](../machines/linux/soccer/README.en.md) |
| Socket | Linux | Medium | WebSocket SQLite, PyInstaller and root build | [ES](../machines/linux/socket/README.md) | [EN](../machines/linux/socket/README.en.md) |
| SolarLab | Windows | Medium | SMB, ReportLab CVE-2023-33733 and OpenFire | [ES](../machines/windows/solarlab/README.md) | [Ver](../machines/windows/solarlab/README.en.md) |
| SolidState | Linux | Medium | Apache James con credenciales por defecto, cron escribible | [ES](../machines/linux/solidstate/README.md) | [Ver](../machines/linux/solidstate/README.en.md) |
| Sorcery | Linux | Insane | Cypher, WebAuthn, Kafka, FreeIPA | [ES](../machines/linux/sorcery/README.md) | [Ver](../machines/linux/sorcery/README.en.md) |
| Soulmate | Linux | Easy | CrushFTP CVE-2025-31161 and Erlang SSH CVE-2025-32433 | [View](../machines/linux/soulmate/README.md) | [EN](../machines/linux/soulmate/README.en.md) |
| Spectra | Linux | Easy | WordPress plugin, auto-login and `initctl` | [View](../machines/linux/spectra/README.en.md) | [ES](../machines/linux/spectra/README.md) |
| Squashed | Linux | Easy | NFS UID spoofing, X11 and `.Xauthority` | [Ver](../machines/linux/squashed/README.md) | [EN](../machines/linux/squashed/README.en.md) |
| Stacked | Linux | Insane | XSS, LocalStack Lambda and Docker socket | [View](../machines/linux/stacked/README.en.md) | [ES](../machines/linux/stacked/README.md) |
| Static | Linux | Hard | TOTP, VPN, xdebug, PHP-FPM CVE-2019-11043 and format string | [ES](../machines/linux/static/README.md) | [EN](../machines/linux/static/README.en.md) |
| Stocker | Linux | Easy | NoSQL injection, PDF file read and `sudo node` | [View](../machines/linux/stocker/README.en.md) | [ES](../machines/linux/stocker/README.md) |
| Stratosphere | Linux | Medium | Struts CVE-2017-5638, MySQL and Python module hijack | [ES](../machines/linux/stratosphere/README.md) | [EN](../machines/linux/stratosphere/README.en.md) |
| StreamIO | Windows | Medium | MSSQL SQLi, LFI/RFI, Firefox and LAPS | [Ver](../machines/windows/streamio/README.md) | [EN](../machines/windows/streamio/README.en.md) |
| Sunday | Solaris | Easy | `finger` user enumeration, cracked shadow and `sudo wget` | [ES](../machines/solaris/sunday/README.md) | [Ver](../machines/solaris/sunday/README.en.md) |
| Support | Windows | Easy | Reversing `UserInfo.exe`, password in `info`, GenericAll over the DC and RBCD | [Ver](../machines/windows/support/README.md) | [EN](../machines/windows/support/README.en.md) |
| Surveillance | Linux | Medium | Craft CMS CVE-2023-41892, SQL backup and ZoneMinder CVE-2023-26035 | [Ver](../machines/linux/surveillance/README.md) | [EN](../machines/linux/surveillance/README.en.md) |
| SwagShop | Linux | Easy | Magento with the Shoplift SQLi, Connect Manager and `sudo vi` | [ES](../machines/linux/swagshop/README.md) | [Ver](../machines/linux/swagshop/README.en.md) |
| Tabby | Linux | Easy | LFI to `tomcat-users.xml`, WAR via `manager/text`, `fcrackzip` and the `lxd` group | [ES](../machines/linux/tabby/README.md) | [Ver](../machines/linux/tabby/README.en.md) |
| Talkative | Linux | Hard | jamovi RCE, Docker pivot and CAP_DAC_READ_SEARCH | [View](../machines/linux/talkative/README.md) | [EN](../machines/linux/talkative/README.en.md) |
| Tally | Windows | Hard | SharePoint, KeePass, MSSQL and SeImpersonate | [View](../machines/windows/tally/README.en.md) | [ES](../machines/windows/tally/README.md) |
| TartarSauce | Linux | Medium | WordPress Gwolle RFI, `tar` wildcard and systemd timer | [ES](../machines/linux/tartarsauce/README.md) | [EN](../machines/linux/tartarsauce/README.en.md) |
| Teacher | Linux | Easy | PNG clue, Moodle PHP injection and backup cron | [View](../machines/linux/teacher/README.en.md) | [ES](../machines/linux/teacher/README.md) |
| Tenet | Linux | Medium | WordPress, PHP object injection and `enableSSH.sh` race | [Ver](../machines/linux/tenet/README.md) | [EN](../machines/linux/tenet/README.en.md) |
| Tentacle | Linux | Hard | Squid/WPAD, OpenSMTPD, Kerberos and keytab | [View](../machines/linux/tentacle/README.en.md) | [ES](../machines/linux/tentacle/README.md) |
| TheFrizz | Windows | Medium | Gibbon CVE-2023-45878, Kerberos and GPO | [ES](../machines/windows/thefrizz/README.md) | [Ver](../machines/windows/thefrizz/README.en.md) |
| TheNotebook | Linux | Medium | JWT `kid`, backup SSH key and runc CVE-2019-5736 | [ES](../machines/linux/thenotebook/README.md) | [Ver](../machines/linux/thenotebook/README.en.md) |
| Time | Linux | Medium | Jackson CVE-2019-12384 and a writable systemd timer | [View](../machines/linux/time/README.en.md) | [ES](../machines/linux/time/README.md) |
| Timelapse | Windows | Easy | Anonymous SMB, PFX, PowerShell history and LAPS up to Administrator | [ES](../machines/windows/timelapse/README.md) | [Ver](../machines/windows/timelapse/README.en.md) |
| Timing | Linux | Medium | LFI, timing attack, mass assignment and `netutils` | [View](../machines/linux/timing/README.en.md) | [ES](../machines/linux/timing/README.md) |
| Titanic | Linux | Easy | Path traversal, Gitea SQLite, hash and ImageMagick CVE-2024-41817 | [Ver](../machines/linux/titanic/README.md) | [EN](../machines/linux/titanic/README.en.md) |
| Toby | Linux | Insane | Theme webshell, Gogs and PAM timing | [View](../machines/linux/toby/README.en.md) | [ES](../machines/linux/toby/README.md) |
| TombWatcher | Windows | Medium | `WriteSPN`, Kerberoasting, gMSA, Recycle Bin and ESC15 | [ES](../machines/windows/tombwatcher/README.md) | [Ver](../machines/windows/tombwatcher/README.en.md) |
| Topology | Linux | Easy | LaTeX injection, `.htpasswd` and root gnuplot cron | [Ver](../machines/linux/topology/README.md) | [EN](../machines/linux/topology/README.en.md) |
| Traceback | Linux | Easy | SmEvK web shell with default credentials, `luvit` via sudo and writable MOTD | [Ver](../machines/linux/traceback/README.md) | [EN](../machines/linux/traceback/README.en.md) |
| Travel | Linux | Hard | Exposed `.git`, memcached PHP object and LDAP | [View](../machines/linux/travel/README.en.md) | [ES](../machines/linux/travel/README.md) |
| Traverxec | Linux | Easy | Nostromo CVE-2019-16278, `.htpasswd` and `journalctl` under sudo | [ES](../machines/linux/traverxec/README.md) | [Ver](../machines/linux/traverxec/README.en.md) |
| Trick | Linux | Easy | AXFR, CVE-2022-28468, LFI with `....//` and fail2ban abuse | [Ver](../machines/linux/trick/README.md) | [EN](../machines/linux/trick/README.en.md) |
| Trickster | Linux | Medium | PrestaShop CVE-2024-34716, SSTI and PrusaSlicer | [ES](../machines/linux/trickster/README.md) | [Ver](../machines/linux/trickster/README.en.md) |
| TwoMillion | Linux | Easy | Invite API, `is_admin`, command injection and overlayfs CVE-2023-0386 | [View](../machines/linux/twomillion/README.en.md) | [ES](../machines/linux/twomillion/README.md) |
| Unattended | Linux | Medium | SQLi, nginx alias, session poisoning and initrd | [ES](../machines/linux/unattended/README.md) | [Ver](../machines/linux/unattended/README.en.md) |
| Unbalanced | Linux | Hard | EncFS, Squid, XPath and Pi-hole | [ES](../machines/linux/unbalanced/README.md) | [EN](../machines/linux/unbalanced/README.en.md) |
| UnderPass | Linux | Easy | SNMP, daloRADIUS and `mosh-server` | [View](../machines/linux/underpass/README.en.md) | [ES](../machines/linux/underpass/README.md) |
| Undetected | Linux | Medium | PHPUnit, backdoor users and Apache module | [ES](../machines/linux/undetected/README.md) | [Ver](../machines/linux/undetected/README.en.md) |
| Unicode | Linux | Medium | JWT `jku`, Unicode traversal and PyInstaller `treport` | [ES](../machines/linux/unicode/README.md) | [Ver](../machines/linux/unicode/README.en.md) |
| University | Windows | Insane | ReportLab CVE-2023-33733, WPAD relay, RBCD, delegation and GMSA | [Ver](../machines/windows/university/README.md) | [EN](../machines/windows/university/README.en.md) |
| Unobtainium | Linux | Hard | Electron/ASAR, LFI, prototype pollution and Kubernetes | [View](../machines/linux/unobtainium/README.en.md) | [ES](../machines/linux/unobtainium/README.md) |
| UpDown | Linux | Medium | SSRF, exposed `.git`, vhosts and `sudo` | [View](../machines/linux/updown/README.en.md) | [ES](../machines/linux/updown/README.md) |
| Usage | Linux | Easy | Blind SQLi, Laravel-Admin and the `7za` wildcard | [ES](../machines/linux/usage/README.md) | [Ver](../machines/linux/usage/README.en.md) |
| Valentine | Linux | Easy | Heartbleed leaks an RSA key passphrase, SSH and a root `tmux` socket | [ES](../machines/linux/valentine/README.md) | [Ver](../machines/linux/valentine/README.en.md) |
| Validation | Linux | Easy | Second-order SQLi, cookies and webshell upload | [Ver](../machines/linux/validation/README.md) | [EN](../machines/linux/validation/README.en.md) |
| VariaType | Linux | Medium | fontTools, FontForge, setuptools | [ES](../machines/linux/variatype/README.md) | [Ver](../machines/linux/variatype/README.en.md) |
| Vault | Linux | Medium | PHP upload, OpenVPN, source-port firewall bypass and GPG | [Ver](../machines/linux/vault/README.md) | [EN](../machines/linux/vault/README.en.md) |
| Vessel | Linux | Hard | `.git`, mysqljs type confusion, OWA CVE-2022-24637 and `pinns` | [Ver](../machines/linux/vessel/README.md) | [EN](../machines/linux/vessel/README.en.md) |
| Vintage | Windows | Hard | Pre-Windows 2000, GMSA, Kerberoast, DPAPI, RBCD and DCSync | [Ver](../machines/windows/vintage/README.md) | [EN](../machines/windows/vintage/README.en.md) |
| Visual | Windows | Medium | Malicious Visual Studio project, XAMPP webshell, FullPowers and GodPotato | [ES](../machines/windows/visual/README.md) | [Ver](../machines/windows/visual/README.en.md) |
| Voleur | Windows | Medium | Access spreadsheet, targeted Kerberoast with `WriteSPN` and tombstone | [Ver](../machines/windows/voleur/README.md) | [EN](../machines/windows/voleur/README.en.md) |
| Waldo | Linux | Medium | PHP file read, SSH key, container, `rbash` escape and `tac` capability | [ES](../machines/linux/waldo/README.md) | [Ver](../machines/linux/waldo/README.en.md) |
| Wall | Linux | Medium | Centreon CVE-2019-13024, WAF bypass with `${IFS}` and SUID `screen` 4.5.0 | [See](../machines/linux/wall/README.md) | [EN](../machines/linux/wall/README.en.md) |
| WhiteRabbit | Linux | Insane | Uptime Kuma, n8n SQLi, restic and timestamp PRNG | [ES](../machines/linux/whiterabbit/README.md) | [Ver](../machines/linux/whiterabbit/README.en.md) |
| WingData | Linux | Easy | Wing FTP CVE-2025-47812 and `tarfile` CVE-2025-4517 | [ES](../machines/linux/wingdata/README.md) | [Ver](../machines/linux/wingdata/README.en.md) |
| Worker | Windows | Medium | SVN history, Azure DevOps, ASPX webshell and the `Setup` pipeline as SYSTEM | [ES](../machines/windows/worker/README.md) | [Ver](../machines/windows/worker/README.en.md) |
| Writeup | Linux | Easy | CMS Made Simple SQLi and `run-parts` | [ES](../machines/linux/writeup/README.md) | [Ver](../machines/linux/writeup/README.en.md) |
| Ypuffy | OpenBSD | Medium | Anonymous LDAP, pass-the-hash and SSH CA | [ES](../machines/openbsd/ypuffy/README.md) | [EN](../machines/openbsd/ypuffy/README.en.md) |
| Yummy | Linux | Hard | ICS traversal, JWT RSA, SQLi to cron, Mercurial and `rsync` | [Ver](../machines/linux/yummy/README.md) | [EN](../machines/linux/yummy/README.en.md) |
| Zetta | Linux | Hard | 32-character FTP, rsync and SQLi in the rsyslog template | [ES](../machines/linux/zetta/README.md) | [Ver](../machines/linux/zetta/README.en.md) |
| Zipper | Linux | Hard | Zabbix API, SUID `zabbix-service` and writable systemd service | [View](../machines/linux/zipper/README.en.md) | [ES](../machines/linux/zipper/README.md) |
| Zipping | Linux | Medium | ZIP symlink, SQLi, webshell and `sudo` binary | [View](../machines/linux/zipping/README.en.md) | [ES](../machines/linux/zipping/README.md) |

## Pending

No retired machine from the plan is left without a writeup.


**Not yet classified:** MonitorsFour, Pirate and Pterodactyl.

## PDF dump

A Spanish-language dump with 164 machine directories, 140 of them holding PDFs (448 PDF and 73 ZIP, ~950 MB). 23 are empty: Ariekei, Bastard, Beep, Brainfuck, Charon, CrimeStoppers, Feline, FluxCapacitor, Fulcrum, Holiday, Inception, Jail, Jeeves, Joker, Lame, Mantis, Minion, Name, Optimum, Shrek, SolidState, Tally, and Smasher (a ZIP only). It is not Markdown: useful as a technique reference, not as text.

## Classification notes

- **PingPong is Insane**, not Hard: the original index files it as Hard, but the weekly drop and several independent sources rate it Insane (Windows, two AD forests).
- **`ref.`** means reference note: the machine was not completed on this profile, so there is no achievement link and no flags are published.
- The cross-inventory of the collections (coverage, duplicates, licences) stays outside the repo in a git-ignored local directory, since it holds third-party material.

## Starting Point (available)

These 25 machines are not retired —they are still available on the platform— but they are catalogued here so the index covers all 235 machine notes in the repository. Details, with tier and service, live in the section index.

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
