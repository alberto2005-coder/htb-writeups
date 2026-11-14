# Catálogo de máquinas retiradas

[🇬🇧 English](catalog.en.md) | **Español**

Fichas de máquinas que sirven para estudiar técnicas. La tabla principal reúne las **retiradas**; al final hay una sección con las 25 de **Starting Point**, que siguen disponibles en la plataforma. Las marcadas como `ref.` no se han jugado en este perfil: son material de estudio, no un logro, y no llevan flags ni credenciales. Las que sí están jugadas viven en `machines/linux/`, `machines/windows/` o `machines/starting-point/` y aparecen en el índice principal.

## Escritas

| Máquina | OS | Dificultad | Técnica principal | ES | EN |
|---|---|---|---|---|---|
| Format | Linux | Medium | Microblog PHP, Gitea, LFI/escritura, Redis por socket y SSTI | [Ver](../machines/linux/format/README.md) | [EN](../machines/linux/format/README.en.md) |
| Agile | Linux | Medium | Flask debug PIN, Chrome debug y sudoedit CVE-2023-22809 | [Ver](../machines/linux/agile/README.md) | [EN](../machines/linux/agile/README.en.md) |
| OnlyForYou | Linux | Medium | LFI absoluto, inyección de comandos con `dig`, Cypher y `pip` como root | [Ver](../machines/linux/onlyforyou/README.md) | [EN](../machines/linux/onlyforyou/README.en.md) |
| Socket | Linux | Medium | WebSocket con SQLite, PyInstaller y build como root | [Ver](../machines/linux/socket/README.md) | [EN](../machines/linux/socket/README.en.md) |
| MonitorsTwo | Linux | Easy | Cacti CVE-2022-46169 y escape Docker CVE-2021-41091 | [Ver](../machines/linux/monitorstwo/README.md) | [EN](../machines/linux/monitorstwo/README.en.md) |
| Aero | Windows | Medium | ThemeBleed CVE-2023-38146 y CLFS CVE-2023-28252 | [Ver](../machines/windows/aero/README.md) | [EN](../machines/windows/aero/README.en.md) |
| Chaffinch | Windows | Medium | GeoServer CVE-2024-36401 y abuso del servicio CSC | [Ver](../machines/windows/chaffinch/README.md) | [EN](../machines/windows/chaffinch/README.en.md) |
| Intentions | Linux | Hard | SQLi de segundo orden, Imagick y `CAP_DAC_READ_SEARCH` | [Ver](../machines/linux/intentions/README.md) | [EN](../machines/linux/intentions/README.en.md) |
| TartarSauce | Linux | Medium | WordPress Gwolle RFI, `tar` con comodín y timer systemd | [Ver](../machines/linux/tartarsauce/README.md) | [EN](../machines/linux/tartarsauce/README.en.md) |
| October | Linux | Medium | October CMS, subida `.php5` y ret2libc con ASLR de 9 bits | [Ver](../machines/linux/october/README.md) | [EN](../machines/linux/october/README.en.md) |
| Jewel | Linux | Medium | GitWeb, Rails y deserialización Redis; TOTP y `sudo gem` | [Ver](../machines/linux/jewel/README.md) | [EN](../machines/linux/jewel/README.en.md) |
| Sneaky | Linux | Medium | SNMP, IPv6, SQLi de login y SUID con overflow | [Ver](../machines/linux/sneaky/README.md) | [EN](../machines/linux/sneaky/README.en.md) |
| Stratosphere | Linux | Medium | Struts CVE-2017-5638, MySQL y secuestro de módulo Python | [Ver](../machines/linux/stratosphere/README.md) | [EN](../machines/linux/stratosphere/README.en.md) |
| Silo | Windows | Medium | Oracle 11g XE, ODAT y ejecución como SYSTEM | [Ver](../machines/windows/silo/README.md) | [EN](../machines/windows/silo/README.en.md) |
| Bart | Windows | Medium | IIS, vhosts, log poisoning y autologon | [Ver](../machines/windows/bart/README.md) | [EN](../machines/windows/bart/README.en.md) |
| Love | Windows | Easy | SSRF, subida PHP y AlwaysInstallElevated | [Ver](../machines/windows/love/README.md) | [EN](../machines/windows/love/README.en.md) |
| Sizzle | Windows | Insane | SCF/Responder, ADCS, Kerberoasting y DCSync | [Ver](../machines/windows/sizzle/README.md) | [EN](../machines/windows/sizzle/README.en.md) |
| Reel | Windows | Hard | RTF CVE-2017-0199, ACL WriteOwner/WriteDacl y script de backup | [Ver](../machines/windows/reel/README.md) | [EN](../machines/windows/reel/README.en.md) |
| Absolute | Windows | Insane | AS-REP, shadow credentials, KrbRelay y DCSync | [Ver](../machines/windows/absolute/README.md) | [EN](../machines/windows/absolute/README.en.md) |
| Multimaster | Windows | Insane | SQLi, CEF debug, GenericWrite/AS-REP y Server Operators | [Ver](../machines/windows/multimaster/README.md) | [EN](../machines/windows/multimaster/README.en.md) |
| Authority | Windows | Medium | SMB anónimo, Ansible Vault, PWM, ESC1 (`CorpVPN`) y PassTheCert | [Ver](../machines/windows/authority/README.md) | [EN](../machines/windows/authority/README.en.md) |
| Sauna | Windows | Easy | AS-REP roasting, credenciales de autologon y DCSync | [Ver](../machines/windows/sauna/README.md) | [EN](../machines/windows/sauna/README.en.md) |
| Netmon | Windows | Easy | FTP anónimo, PRTG y CVE-2018-9276 | [Ver](../machines/windows/netmon/README.md) | [EN](../machines/windows/netmon/README.en.md) |
| Servmon | Windows | Easy | NVMS path traversal, NSClient++ y túnel SSH | [Ver](../machines/windows/servmon/README.md) | [EN](../machines/windows/servmon/README.en.md) |
| Resolute | Windows | Medium | LDAP anónimo, reutilización y `DnsAdmins` | [Ver](../machines/windows/resolute/README.md) | [EN](../machines/windows/resolute/README.en.md) |
| Bastard | Windows | Medium | Drupalgeddon2 y JuicyPotato | [Ver](../machines/windows/bastard/README.md) | [EN](../machines/windows/bastard/README.en.md) |
| Cap | Linux | Easy | IDOR, pcap, `cap_setuid` | [Ver](../machines/linux/cap/README.md) | [EN](../machines/linux/cap/README.en.md) |
| Active | Windows | Easy | GPP en SYSVOL, Kerberoasting a `Administrator` | [Ver](../machines/windows/active/README.md) | [EN](../machines/windows/active/README.en.md) |
| Armageddon | Linux | Easy | Drupal 7.56, Drupalgeddon2, hook de snap | [Ver](../machines/linux/armageddon/README.md) | [EN](../machines/linux/armageddon/README.en.md) |
| Bashed | Linux | Easy | webshell `phpbash`, `sudo -u`, cron de root | [Ver](../machines/linux/bashed/README.md) | [EN](../machines/linux/bashed/README.en.md) |
| Bastion | Windows | Easy | backup SMB con VHDX, SAM/SYSTEM, mRemoteNG | [Ver](../machines/windows/bastion/README.md) | [EN](../machines/windows/bastion/README.en.md) |
| Beep | Linux | Easy | LFI en Elastix, CVE-2012-4869, `nmap` interactivo | [Ver](../machines/linux/beep/README.md) | [EN](../machines/linux/beep/README.en.md) |
| Blocky | Linux | Easy | credenciales en un JAR, reutilización, `sudo ALL` | [Ver](../machines/linux/blocky/README.md) | [EN](../machines/linux/blocky/README.en.md) |
| Blunder | Linux | Easy | Bludit, bypass de fuerza bruta, `sudo -u#-1` | [Ver](../machines/linux/blunder/README.md) | [EN](../machines/linux/blunder/README.en.md) |
| Bounty | Windows | Easy | `web.config` en IIS, `SeImpersonate`, JuicyPotato | [Ver](../machines/windows/bounty/README.md) | [EN](../machines/windows/bounty/README.en.md) |
| Delivery | Linux | Easy | osTicket + Mattermost, bcrypt con reglas | [Ver](../machines/linux/delivery/README.md) | [EN](../machines/linux/delivery/README.en.md) |
| Facts | Linux | Easy | Camaleon CMS, MinIO, clave SSH, `facter` | [Ver](../machines/linux/facts/README.md) | [EN](../machines/linux/facts/README.en.md) |
| Forest | Windows | Easy | AS-REP, `Account Operators` → Exchange, DCSync | [Ver](../machines/windows/forest/README.md) | [EN](../machines/windows/forest/README.en.md) |
| FriendZone | Linux | Easy | AXFR, LFI + SMB, hijack de `os.py` | [Ver](../machines/linux/friendzone/README.md) | [EN](../machines/linux/friendzone/README.en.md) |
| Admirer | Linux | Easy | Adminer 4.6.2, LFI con MySQL propio, `PYTHONPATH` | [Ver](../machines/linux/admirer/README.md) | [EN](../machines/linux/admirer/README.en.md) |
| Arctic | Windows | Easy | ColdFusion 8 + FCKeditor, JuicyPotato | [Ver](../machines/windows/arctic/README.md) | [EN](../machines/windows/arctic/README.en.md) |
| Bank | Linux | Easy | AXFR, `302` a `200`, subida `.htb`, SUID | [Ver](../machines/linux/bank/README.md) | [EN](../machines/linux/bank/README.en.md) |
| Blue | Windows | Easy | MS17-010 EternalBlue | [Ver](../machines/windows/blue/README.md) | [EN](../machines/windows/blue/README.en.md) |
| Cronos | Linux | Medium | AXFR, SQLi, inyección de comandos, cron de `artisan` | [Ver](../machines/linux/cronos/README.md) | [EN](../machines/linux/cronos/README.en.md) |
| PingPong | Windows | Insane | Dos bosques AD, ESC13, pivote, gMSA, JEA, RBCD y ESC4→ESC1 | [Ver](../machines/windows/pingpong/README.md) | [EN](../machines/windows/pingpong/README.en.md) |
| AirTouch | Linux | Medium | WPA2, Evil Twin PEAP, pivote VPN | [Ver](../machines/linux/airtouch/README.md) | [EN](../machines/linux/airtouch/README.en.md) |
| Eighteen | Windows | Hard | `IMPERSONATE`, Werkzeug, CVE-2025-53779 | [Ver](../machines/windows/eighteen/README.md) | [EN](../machines/windows/eighteen/README.en.md) |
| Sink | Linux | Insane | Smuggling, Gitea, AWS KMS | [Ver](../machines/linux/sink/README.md) | [EN](../machines/linux/sink/README.en.md) |
| Sorcery | Linux | Insane | Cypher, WebAuthn, Kafka, FreeIPA | [Ver](../machines/linux/sorcery/README.md) | [EN](../machines/linux/sorcery/README.en.md) |
| Cobblestone | Linux | Insane | SQLi de segundo orden, Twig SSTI, Cobbler | [Ver](../machines/linux/cobblestone/README.md) | [EN](../machines/linux/cobblestone/README.en.md) |
| Code | Linux | Easy | Escape de sandbox Python, bcrypt, `backy.sh` | [Ver](../machines/linux/code/README.md) | [EN](../machines/linux/code/README.en.md) |
| Kobold | Linux | Easy | MCPJam CVE-2026-23744, PrivateBin, Docker | [Ver](../machines/linux/kobold/README.md) | [EN](../machines/linux/kobold/README.en.md) |
| Helix | Linux | Medium | NiFi + H2 `CREATE ALIAS`, OPC UA | [Ver](../machines/linux/helix/README.md) | [EN](../machines/linux/helix/README.en.md) |
| Interpreter | Linux | Medium | Mirth CVE-2023-43208, PBKDF2, `eval()` | [Ver](../machines/linux/interpreter/README.md) | [EN](../machines/linux/interpreter/README.en.md) |
| VariaType | Linux | Medium | fontTools, FontForge, setuptools | [Ver](../machines/linux/variatype/README.md) | [EN](../machines/linux/variatype/README.en.md) |
| Pirate | Windows | Hard | Pre-Windows 2000, gMSA, RBCD, S4U2Proxy | [Ver](../machines/windows/pirate/README.md) | [EN](../machines/windows/pirate/README.en.md) |
| MonitorsFour | Windows | Easy | IDOR en la API, MD5 crackeado, CVE-2025-24367 en Cacti, escape por la API de Docker | [Ver](../machines/windows/monitorsfour/README.md) | [EN](../machines/windows/monitorsfour/README.en.md) |
| Pterodactyl | Linux | Medium | CVE-2025-49132 en `/locales`, PEAR `pearcmd`, cadena CVE-2025-6018/6019 | [Ver](../machines/linux/pterodactyl/README.md) | [EN](../machines/linux/pterodactyl/README.en.md) |
| Buff | Windows | Easy | Subida sin autenticacion, CloudMe 1.11.2 | [Ver](../machines/windows/buff/README.md) | [EN](../machines/windows/buff/README.en.md) |
| Blackfield | Windows | Hard | AS-REP, volcado de lsass, SeBackupPrivilege, NTDS | [Ver](../machines/windows/blackfield/README.md) | [EN](../machines/windows/blackfield/README.en.md) |
| Nibbles | Linux | Easy | Nibbleblog 4.0.3, subida CVE-2015-6967, sudo | [Ver](../machines/linux/nibbles/README.md) | [EN](../machines/linux/nibbles/README.en.md) |
| Doctor | Linux | Easy | SSTI con Jinja2 en un vhost, Splunk 8.0.x | [Ver](../machines/linux/doctor/README.md) | [EN](../machines/linux/doctor/README.en.md) |
| Poison | FreeBSD | Medium | LFI en `browse.php`, base64 en `pwdbackup.txt`, VNC como root con `secret.zip` | [Ver](../machines/freebsd/poison/README.md) | [EN](../machines/freebsd/poison/README.en.md) |
| SolidState | Linux | Medium | Apache James con credenciales por defecto, cron escribible | [Ver](../machines/linux/solidstate/README.md) | [EN](../machines/linux/solidstate/README.en.md) |
| DevOops | Linux | Medium | XXE en la subida de XML y clave de root en el historial de git | [Ver](../machines/linux/devoops/README.md) | [EN](../machines/linux/devoops/README.en.md) |
| Frolic | Linux | Easy | Login en JS, PlaySMS 1.4 con CSV, SUID `rop` con ret2libc | [Ver](../machines/linux/frolic/README.md) | [EN](../machines/linux/frolic/README.en.md) |
| Sea | Linux | Easy | WonderCMS CVE-2023-41425, hash crackeado, inyección de comandos en el 8080 | [Ver](../machines/linux/sea/README.md) | [EN](../machines/linux/sea/README.en.md) |
| Devel | Windows | Easy | FTP anónimo escribible sobre IIS, webshell ASPX, MS10-015 / `SeImpersonate` | [Ver](../machines/windows/devel/README.md) | [EN](../machines/windows/devel/README.en.md) |
| Fluffy | Windows | Easy | CVE-2025-24071, shadow credentials, ADCS ESC16 | [Ver](../machines/windows/fluffy/README.md) | [EN](../machines/windows/fluffy/README.en.md) |
| Garfield | Windows | Hard | RODC, ticket dorado con KeyList, secretsdump, pass-the-hash | [Ver](../machines/windows/garfield/README.md) | [EN](../machines/windows/garfield/README.en.md) |
| Academy | Linux | Easy | Roleid → Laravel CVE-2018-15133 con `APP_KEY`, `.env` y `composer` por sudo | [Ver](../machines/linux/academy/README.md) | [EN](../machines/linux/academy/README.en.md) |
| Apocalyst | Linux | Medium | WordPress, `cewl` y `steghide`, hydra, plugin PHP y `/etc/passwd` escribible | [Ver](../machines/linux/apocalyst/README.md) | [EN](../machines/linux/apocalyst/README.en.md) |
| OpenAdmin | Linux | Easy | OpenNetAdmin 18.1.1, reutilización de credenciales, `ssh2john` y escape de `nano` | [Ver](../machines/linux/openadmin/README.md) | [EN](../machines/linux/openadmin/README.en.md) |
| Tabby | Linux | Easy | LFI a `tomcat-users.xml`, WAR por `manager/text`, `fcrackzip` y grupo `lxd` | [Ver](../machines/linux/tabby/README.md) | [EN](../machines/linux/tabby/README.en.md) |
| Jerry | Windows | Easy | Tomcat 7 con credenciales por defecto, WAR por `/manager/text` y shell directa como SYSTEM | [Ver](../machines/windows/jerry/README.md) | [EN](../machines/windows/jerry/README.en.md) |
| Chatterbox | Windows | Medium | Desbordamiento en AChat 0.150 (EDB 36025) y AutoLogon en el registro | [Ver](../machines/windows/chatterbox/README.md) | [EN](../machines/windows/chatterbox/README.en.md) |
| Heist | Windows | Easy | Config de Cisco con type 7 y type 5, spray a WinRM y `procdump` sobre Firefox | [Ver](../machines/windows/heist/README.md) | [EN](../machines/windows/heist/README.en.md) |
| Valentine | Linux | Easy | Heartbleed filtra la passphrase de una clave RSA, SSH y socket de `tmux` de root | [Ver](../machines/linux/valentine/README.md) | [EN](../machines/linux/valentine/README.en.md) |
| Shocker | Linux | Easy | Shellshock en un CGI (`user.sh`) y `sudo perl` de GTFOBins | [Ver](../machines/linux/shocker/README.md) | [EN](../machines/linux/shocker/README.en.md) |
| SwagShop | Linux | Easy | Magento con SQLi Shoplift, Connect Manager y `sudo vi` | [Ver](../machines/linux/swagshop/README.md) | [EN](../machines/linux/swagshop/README.en.md) |
| Networked | Linux | Easy | Backup con el código, doble extensión, cron inyectable y `sudo` sin comillas | [Ver](../machines/linux/networked/README.md) | [EN](../machines/linux/networked/README.en.md) |
| Sense | FreeBSD | Easy | pfSense 2.1.3 con credenciales por defecto y CVE-2014-4688 como root | [Ver](../machines/freebsd/sense/README.md) | [EN](../machines/freebsd/sense/README.en.md) |
| Legacy | Windows | Easy | MS08-067 sobre SMBv1 en Windows XP | [Ver](../machines/windows/legacy/README.md) | [EN](../machines/windows/legacy/README.en.md) |
| Sunday | Solaris | Easy | `finger` para enumerar usuarios, shadow crackeado y `sudo wget` | [Ver](../machines/solaris/sunday/README.md) | [EN](../machines/solaris/sunday/README.en.md) |
| Lame | Linux | Easy | Samba `usermap_script` (CVE-2007-2447) para root directo; `distcc` y `vsftpd` como alternativas | [Ver](../machines/linux/lame/README.md) | [EN](../machines/linux/lame/README.en.md) |
| Optimum | Windows | Easy | Rejetto HFS 2.3 (CVE-2014-6287) y MS16-032 hasta SYSTEM | [Ver](../machines/windows/optimum/README.md) | [EN](../machines/windows/optimum/README.en.md) |
| Sau | Linux | Easy | SSRF en Request Baskets hacia Maltrail y `sudo systemctl` con escape del pager | [Ver](../machines/linux/sau/README.md) | [EN](../machines/linux/sau/README.en.md) |
| Nineveh | Linux | Medium | phpLiteAdmin + LFI, port knocking y chkrootkit 0.49 como root | [Ver](../machines/linux/nineveh/README.md) | [EN](../machines/linux/nineveh/README.en.md) |
| Jeeves | Windows | Medium | Jenkins sin autenticación, KeePass, pass-the-hash y flag en un flujo NTFS | [Ver](../machines/windows/jeeves/README.md) | [EN](../machines/windows/jeeves/README.en.md) |
| CozyHosting | Linux | Easy | Actuator que filtra sesiones, inyección de comandos en el panel, PostgreSQL y `sudo ssh` | [Ver](../machines/linux/cozyhosting/README.md) | [EN](../machines/linux/cozyhosting/README.en.md) |
| BoardLight | Linux | Easy | Dolibarr 17.0.0 con credenciales por defecto, CVE-2023-30253 y SUID de Enlightenment | [Ver](../machines/linux/boardlight/README.md) | [EN](../machines/linux/boardlight/README.en.md) |
| Busqueda | Linux | Easy | `eval()` de Searchor, `.git` con credenciales, Gitea y `full-checkup.sh` relativo | [Ver](../machines/linux/busqueda/README.md) | [EN](../machines/linux/busqueda/README.en.md) |
| Soccer | Linux | Easy | Tiny File Manager por defecto, SQLi ciega por WebSocket y `doas` con `dstat` | [Ver](../machines/linux/soccer/README.md) | [EN](../machines/linux/soccer/README.en.md) |
| Timelapse | Windows | Easy | SMB anónimo, PFX, historial de PowerShell y LAPS hasta Administrator | [Ver](../machines/windows/timelapse/README.md) | [EN](../machines/windows/timelapse/README.en.md) |
| Cicada | Windows | Easy | SMB de invitado, contraseña de onboarding, spray y `SeBackupPrivilege` | [Ver](../machines/windows/cicada/README.md) | [EN](../machines/windows/cicada/README.en.md) |
| Support | Windows | Easy | Reversing de `UserInfo.exe`, contraseña en `info`, GenericAll sobre el DC y RBCD | [Ver](../machines/windows/support/README.md) | [EN](../machines/windows/support/README.en.md) |
| Administrator | Windows | Medium | ACLs hasta FTP, `.psafe3`, targeted kerberoasting y DCSync | [Ver](../machines/windows/administrator/README.md) | [EN](../machines/windows/administrator/README.en.md) |
| Escape | Windows | Medium | PDF con credenciales MSSQL, `xp_dirtree` y ADCS ESC1 | [Ver](../machines/windows/escape/README.md) | [EN](../machines/windows/escape/README.en.md) |
| Pilgrimage | Linux | Easy | `/.git`, ImageMagick CVE-2022-44268 y binwalk CVE-2022-4510 | [Ver](../machines/linux/pilgrimage/README.md) | [EN](../machines/linux/pilgrimage/README.en.md) |
| MakeSense | Linux | Medium | Season 11: XSS al bot admin, AES-GCM forjado, plugin malicioso y OCR como root | [Ver](../machines/linux/makesense/README.md) | [EN](../machines/linux/makesense/README.en.md) |
| Cascade | Windows | Medium | LDAP anónimo, `cascadeLegacyPwd`, VNC reversible y AD Recycle Bin | [Ver](../machines/windows/cascade/README.md) | [EN](../machines/windows/cascade/README.en.md) |
| Traceback | Linux | Easy | Webshell SmEvK con credenciales por defecto, `luvit` por sudo y MOTD escribible | [Ver](../machines/linux/traceback/README.md) | [EN](../machines/linux/traceback/README.en.md) |
| Craft | Linux | Easy | `eval()` en Flask, historial de Gogs, MySQL en claro y OTP de Vault | [Ver](../machines/linux/craft/README.md) | [EN](../machines/linux/craft/README.en.md) |
| Book | Linux | Medium | Truncado SQL en el registro, XSS en el PDF y carrera de `logrotate` | [Ver](../machines/linux/book/README.md) | [EN](../machines/linux/book/README.en.md) |
| Querier | Windows | Medium | Macro con credenciales, `xp_dirtree`, NetNTLMv2 y GPP | [Ver](../machines/windows/querier/README.md) | [EN](../machines/windows/querier/README.en.md) |
| Remote | Windows | Medium | NFS con el backup de Umbraco, SHA1, RCE XSLT y TeamViewer | [Ver](../machines/windows/remote/README.md) | [EN](../machines/windows/remote/README.en.md) |
| Luke | FreeBSD | Medium | `config.php` en claro, API con JWT y Ajenti como root | [Ver](../machines/freebsd/luke/README.md) | [EN](../machines/freebsd/luke/README.en.md) |
| Mantis | Windows | Hard | Orchard CMS, MSSQL y MS14-068 (PAC forjado) | [Ver](../machines/windows/mantis/README.md) | [EN](../machines/windows/mantis/README.en.md) |
| Return | Windows | Easy | Panel de impresora, bind LDAP, WinRM y `Server Operators` | [Ver](../machines/windows/return/README.md) | [EN](../machines/windows/return/README.en.md) |
| Retired | Linux | Medium | File read, ROP, symlink en backup y `binfmt_misc` | [Ver](../machines/linux/retired/README.md) | [EN](../machines/linux/retired/README.en.md) |
| Vault | Linux | Medium | Upload PHP, OpenVPN, firewall por puerto origen y GPG | [Ver](../machines/linux/vault/README.md) | [EN](../machines/linux/vault/README.en.md) |
| Flight | Windows | Hard | LFI en `school.flight.htb`, Responder, share SMB y DCSync con Rubeus | [Ver](../machines/windows/flight/README.md) | [EN](../machines/windows/flight/README.en.md) |
| Trick | Linux | Easy | AXFR, CVE-2022-28468, LFI con `....//` y abuso de fail2ban | [Ver](../machines/linux/trick/README.md) | [EN](../machines/linux/trick/README.en.md) |
| BroScience | Linux | Medium | LFI `img.php?path=`, doble URL-encode, `AvatarInterface` y hashcat `-m 20` | [Ver](../machines/linux/broscience/README.md) | [EN](../machines/linux/broscience/README.en.md) |
| Outdated | Windows | Medium | Follina CVE-2022-30190, shadow credentials y abuso de WSUS | [Ver](../machines/windows/outdated/README.md) | [EN](../machines/windows/outdated/README.en.md) |
| Scrambled | Windows | Medium | Kerberoast `sqlsvc`, silver ticket y `BinaryFormatter` en `ScrambleClient.exe` | [Ver](../machines/windows/scrambled/README.md) | [EN](../machines/windows/scrambled/README.en.md) |
| Baby | Windows | Easy | Credencial en LDAP, spray, `Backup Operators` y volcado de NTDS | [Ver](../machines/windows/baby/README.md) | [EN](../machines/windows/baby/README.en.md) |
| Voleur | Windows | Medium | Excel de accesos, Kerberoast dirigido con `WriteSPN` y tombstone | [Ver](../machines/windows/voleur/README.md) | [EN](../machines/windows/voleur/README.en.md) |
| Rainbow | Windows | Medium | FTP anónimo, reinicio del servicio y bypass de UAC con `fodhelper` | [Ver](../machines/windows/rainbow/README.md) | [EN](../machines/windows/rainbow/README.en.md) |
| RetroTwo | Windows | Easy | Macro en Access, cuentas Pre-Windows 2000 y ZeroLogon | [Ver](../machines/windows/retrotwo/README.md) | [EN](../machines/windows/retrotwo/README.en.md) |
| Certified | Windows | Medium | `WriteOwner`/`GenericAll` y AD CS ESC9 | [Ver](../machines/windows/certified/README.md) | [EN](../machines/windows/certified/README.en.md) |
| Era | Linux | Medium | IDOR en backups, módulo SSH y binario firmado ejecutado por cron | [Ver](../machines/linux/era/README.md) | [EN](../machines/linux/era/README.en.md) |
| Build | Linux | Medium | Backup de Jenkins por rsync, pipeline de Gitea y rlogin | [Ver](../machines/linux/build/README.md) | [EN](../machines/linux/build/README.en.md) |
| Forgotten | Linux | Easy | Instalador de LimeSurvey, plugin malicioso y reutilización de secretos | [Ver](../machines/linux/forgotten/README.md) | [EN](../machines/linux/forgotten/README.en.md) |
| Analytics | Linux | Easy | Metabase CVE-2023-38646, credenciales en el contenedor y overlayfs | [Ver](../machines/linux/analytics/README.md) | [EN](../machines/linux/analytics/README.en.md) |
| Devvortex | Linux | Easy | API de Joomla CVE-2023-23752, plantilla PHP y `apport-cli` | [Ver](../machines/linux/devvortex/README.md) | [EN](../machines/linux/devvortex/README.en.md) |
| Horizontall | Linux | Easy | Strapi CVE-2019-19609 y Laravel Ignition CVE-2021-3129 por túnel | [Ver](../machines/linux/horizontall/README.md) | [EN](../machines/linux/horizontall/README.en.md) |
| Photobomb | Linux | Easy | Credenciales en JavaScript, inyección en `filetype` y PATH hijack | [Ver](../machines/linux/photobomb/README.md) | [EN](../machines/linux/photobomb/README.en.md) |
| Granny | Windows | Easy | WebDAV `PUT`/`MOVE`, webshell ASPX y Churrasco | [Ver](../machines/windows/granny/README.md) | [EN](../machines/windows/granny/README.en.md) |
| Grandpa | Windows | Easy | IIS 6.0 CVE-2017-7269 y elevación con Churrasco | [Ver](../machines/windows/grandpa/README.md) | [EN](../machines/windows/grandpa/README.en.md) |
| SecNotes | Windows | Medium | CSRF al admin, webshell por SMB y WSL `bash.exe` | [Ver](../machines/windows/secnotes/README.md) | [EN](../machines/windows/secnotes/README.en.md) |
| Monteverde | Windows | Medium | LDAP anónimo, `azure.xml` y credenciales de Azure AD Connect | [Ver](../machines/windows/monteverde/README.md) | [EN](../machines/windows/monteverde/README.en.md) |
| Keeper | Linux | Easy | Request Tracker por defecto, ticket con credenciales y KeePass CVE-2023-32784 | [Ver](../machines/linux/keeper/README.md) | [EN](../machines/linux/keeper/README.en.md) |
| Validation | Linux | Easy | SQLi de segundo orden, cookies y subida de webshell | [Ver](../machines/linux/validation/README.md) | [EN](../machines/linux/validation/README.en.md) |
| Paper | Linux | Medium | Borrador de WordPress, Rocket.Chat CVE-2019-17671 y polkit | [Ver](../machines/linux/paper/README.md) | [EN](../machines/linux/paper/README.en.md) |
| Pandora | Linux | Medium | SNMP, SQLi en Pandora FMS y PATH hijack con SUID | [Ver](../machines/linux/pandora/README.md) | [EN](../machines/linux/pandora/README.en.md) |
| Giddy | Windows | Medium | SQLi en IIS, WinRM y UniFi Video como SYSTEM | [Ver](../machines/windows/giddy/README.md) | [EN](../machines/windows/giddy/README.en.md) |
| Sniper | Windows | Medium | LFI/RFI, SMB y `runas /savecred` | [Ver](../machines/windows/sniper/README.md) | [EN](../machines/windows/sniper/README.en.md) |
| StreamIO | Windows | Medium | SQLi MSSQL, LFI/RFI, Firefox y LAPS | [Ver](../machines/windows/streamio/README.md) | [EN](../machines/windows/streamio/README.en.md) |
| Conceal | Windows | Hard | SNMP/IPsec, FTP anónimo con webshell y JuicyPotato | [Ver](../machines/windows/conceal/README.md) | [EN](../machines/windows/conceal/README.en.md) |
| Jarvis | Linux | Medium | SQLi, phpMyAdmin CVE-2018-12613 y `systemctl` SUID | [Ver](../machines/linux/jarvis/README.md) | [EN](../machines/linux/jarvis/README.en.md) |
| Meta | Linux | Medium | ExifTool CVE-2021-22204 y cron editable | [Ver](../machines/linux/meta/README.md) | [EN](../machines/linux/meta/README.en.md) |
| Sandworm | Linux | Medium | SSTI, Firejail, crate Rust y CVE-2022-31214 | [Ver](../machines/linux/sandworm/README.md) | [EN](../machines/linux/sandworm/README.en.md) |
| Ambassador | Linux | Medium | Grafana CVE-2021-43798, `grafana.db` y Consul | [Ver](../machines/linux/ambassador/README.md) | [EN](../machines/linux/ambassador/README.en.md) |
| Squashed | Linux | Easy | NFS con UID spoofing, X11 y `.Xauthority` | [Ver](../machines/linux/squashed/README.md) | [EN](../machines/linux/squashed/README.en.md) |
| Mailing | Windows | Easy | LFI a hMailServer, MonikerLink y macro | [Ver](../machines/windows/mailing/README.md) | [EN](../machines/windows/mailing/README.en.md) |
| Certificate | Windows | Hard | ADCS ESC3, Golden Certificate y EFS | [Ver](../machines/windows/certificate/README.md) | [EN](../machines/windows/certificate/README.en.md) |
| Search | Windows | Hard | Credenciales en imagen, WDigest, gMSA y NTDS | [Ver](../machines/windows/search/README.md) | [EN](../machines/windows/search/README.en.md) |
| PermX | Linux | Easy | Chamilo CVE-2023-4220, credenciales y `setfacl` con symlink | [Ver](../machines/linux/permx/README.md) | [EN](../machines/linux/permx/README.en.md) |
| GreenHorn | Linux | Easy | Pluck CMS, Gitea expuesto y Depix | [Ver](../machines/linux/greenhorn/README.md) | [EN](../machines/linux/greenhorn/README.en.md) |
| LinkVortex | Linux | Easy | `.git`, Ghost CVE-2023-40028 y TOCTOU | [Ver](../machines/linux/linkvortex/README.md) | [EN](../machines/linux/linkvortex/README.en.md) |
| EscapeTwo | Windows | Easy | Excel, MSSQL, `WriteOwner` y ADCS ESC4 a ESC1 | [Ver](../machines/windows/escapetwo/README.md) | [EN](../machines/windows/escapetwo/README.en.md) |
| TombWatcher | Windows | Medium | `WriteSPN`, Kerberoasting, gMSA, Recycle Bin y ESC15 | [Ver](../machines/windows/tombwatcher/README.md) | [EN](../machines/windows/tombwatcher/README.en.md) |
| Planning | Linux | Easy | Grafana CVE-2024-9264, credenciales y Crontab UI | [Ver](../machines/linux/planning/README.md) | [EN](../machines/linux/planning/README.en.md) |
| Data | Linux | Easy | Grafana CVE-2021-43798, hash PBKDF2 y Docker privilegiado | [Ver](../machines/linux/data/README.md) | [EN](../machines/linux/data/README.en.md) |
| Sightless | Linux | Easy | SQLPad CVE-2022-0944, Froxlor y WebDriver | [Ver](../machines/linux/sightless/README.md) | [EN](../machines/linux/sightless/README.en.md) |
| Editor | Linux | Medium | XWiki CVE-2025-24893 y NetData `ndsudo` | [Ver](../machines/linux/editor/README.md) | [EN](../machines/linux/editor/README.en.md) |
| Conversor | Linux | Medium | `os.path.join`, cron de scripts y `needrestart` | [Ver](../machines/linux/conversor/README.md) | [EN](../machines/linux/conversor/README.en.md) |
| Hospital | Windows | Medium | `.phar`, CVE-2023-35001, Ghostscript y XAMPP | [Ver](../machines/windows/hospital/README.md) | [EN](../machines/windows/hospital/README.en.md) |
| TheFrizz | Windows | Medium | Gibbon CVE-2023-45878, Kerberos y GPO | [Ver](../machines/windows/thefrizz/README.md) | [EN](../machines/windows/thefrizz/README.en.md) |
| Haze | Windows | Hard | Splunk CVE-2024-36991, gMSA y shadow credentials | [Ver](../machines/windows/haze/README.md) | [EN](../machines/windows/haze/README.en.md) |
| Node | Linux | Medium | API `/api/users/latest` con hashes, backup ZIP, SSH `mark`, tareas MongoDB y SUID `backup` con BOF | [Ver](../machines/linux/node/README.md) | [EN](../machines/linux/node/README.en.md) |
| Celestial | Linux | Medium | Cookie base64 con `node-serialize`, RCE como `sun` y cron que restaura el script | [Ver](../machines/linux/celestial/README.md) | [EN](../machines/linux/celestial/README.en.md) |
| Mirai | Linux | Easy | Pi-hole/Plex, credenciales por defecto, `sudo ALL` y flag borrada recuperada del USB | [Ver](../machines/linux/mirai/README.md) | [EN](../machines/linux/mirai/README.en.md) |
| Irked | Linux | Easy | UnrealIRCd 3.2.8.1, `AB;`, steghide, SSH y SUID `viewuser` | [Ver](../machines/linux/irked/README.md) | [EN](../machines/linux/irked/README.en.md) |
| Fuse | Windows | Medium | PaperCut, `cewl`/spray, RPC `svc-print`, WinRM y Capcom.sys | [Ver](../machines/windows/fuse/README.md) | [EN](../machines/windows/fuse/README.en.md) |
| Nest | Windows | Easy | SMB invitado, `RU_config.xml`, descifrado VB, `c.smith`, ADS y `psexec` | [Ver](../machines/windows/nest/README.md) | [EN](../machines/windows/nest/README.en.md) |
| Omni | Windows | Easy | Windows IoT Core, SirepRAT, `reg save`, WDP y `Import-Clixml` | [Ver](../machines/windows/omni/README.md) | [EN](../machines/windows/omni/README.en.md) |
| Worker | Windows | Medium | Historial SVN, Azure DevOps, webshell ASPX y pipeline `Setup` como SYSTEM | [Ver](../machines/windows/worker/README.md) | [EN](../machines/windows/worker/README.en.md) |

| Precious | Linux | Easy | PDFKit SSRF, lectura de archivos y YAML con `sudo` | [Ver](../machines/linux/precious/README.md) | [EN](../machines/linux/precious/README.en.md) |
| UpDown | Linux | Medium | SSRF, `.git` expuesto, vhosts y `sudo` | [Ver](../machines/linux/updown/README.md) | [EN](../machines/linux/updown/README.en.md) |
| Zipping | Linux | Medium | ZIP con symlink, SQLi, webshell y binario con `sudo` | [Ver](../machines/linux/zipping/README.md) | [EN](../machines/linux/zipping/README.en.md) |
| Health | Linux | Medium | Redirección SSRF, Gogs con SQLi y cron como root | [Ver](../machines/linux/health/README.md) | [EN](../machines/linux/health/README.en.md) |
| SneakyMailer | Linux | Medium | SMTP, phishing, IMAP, FTP y paquete PyPI | [Ver](../machines/linux/sneakymailer/README.md) | [EN](../machines/linux/sneakymailer/README.en.md) |
| Catch | Linux | Medium | APK, secretos en Gitea y Let's Chat | [Ver](../machines/linux/catch/README.md) | [EN](../machines/linux/catch/README.en.md) |
| Driver | Windows | Easy | `.scf`/Responder, WinRM y PrintNightmare | [Ver](../machines/windows/driver/README.md) | [EN](../machines/windows/driver/README.en.md) |
| Anubis | Windows | Insane | ASP, Jamovi, ADCS ESC y PKINIT | [Ver](../machines/windows/anubis/README.md) | [EN](../machines/windows/anubis/README.en.md) |

## Pendientes

1 máquina retirada con material localizado y todavía sin ficha propia.

**Linux:** DevArea.


## Volcado en PDF

Un volcado en español de 164 directorios de máquina, 140 con PDF (448 PDF y 73 ZIP, ~950 MB). 23 están vacíos: Ariekei, Bastard, Beep, Brainfuck, Charon, CrimeStoppers, Feline, FluxCapacitor, Fulcrum, Holiday, Inception, Jail, Jeeves, Joker, Lame, Mantis, Minion, Name, Optimum, Shrek, SolidState, Tally, y Smasher (solo un ZIP). No es Markdown: sirve como referencia de técnicas, no como texto.

## Notas de clasificación

- **PingPong es Insane**, no Hard: el índice de origen lo lista como Hard, pero el lanzamiento semanal y varias fuentes independientes lo dan como Insane (Windows, dos bosques de AD).
- **`ref.`** significa ficha de referencia: la máquina no se ha completado en este perfil, así que no hay enlace de logro ni se publican flags.
- El inventario cruzado de las colecciones (cobertura, duplicados, licencias) queda fuera del repo, en un directorio local ignorado por git, porque incluye material de terceros.

## Starting Point (disponibles)

Estas 25 máquinas no están retiradas —siguen disponibles en la plataforma— pero se catalogan aquí para que el índice cubra las 202 fichas del repositorio. El detalle, con tier y servicio, está en el índice de la sección.

| Máquina | OS | Dificultad | Técnica principal | ES | EN |
|---|---|---|---|---|---|
| Meow | Linux | Very Easy | Telnet con `root` sin contraseña | [Ver](../machines/starting-point/meow/README.md) | [EN](../machines/starting-point/meow/README.en.md) |
| Fawn | Linux | Very Easy | FTP anónimo y `get flag.txt` | [Ver](../machines/starting-point/fawn/README.md) | [EN](../machines/starting-point/fawn/README.en.md) |
| Dancing | Windows | Very Easy | SMB nulo y share `WorkShares` | [Ver](../machines/starting-point/dancing/README.md) | [EN](../machines/starting-point/dancing/README.en.md) |
| Redeemer | Linux | Very Easy | Redis sin `AUTH` | [Ver](../machines/starting-point/redeemer/README.md) | [EN](../machines/starting-point/redeemer/README.en.md) |
| Explosion | Windows | Very Easy | RDP con `Administrator` vacío | [Ver](../machines/starting-point/explosion/README.md) | [EN](../machines/starting-point/explosion/README.en.md) |
| Preignition | Linux | Very Easy | `/admin.php` con `admin:admin` | [Ver](../machines/starting-point/preignition/README.md) | [EN](../machines/starting-point/preignition/README.en.md) |
| Mongod | Linux | Very Easy | MongoDB sin `--auth` | [Ver](../machines/starting-point/mongod/README.md) | [EN](../machines/starting-point/mongod/README.en.md) |
| Synced | Linux | Very Easy | rsync anónimo en 873 | [Ver](../machines/starting-point/synced/README.md) | [EN](../machines/starting-point/synced/README.en.md) |
| Sequel | Linux | Very Easy | MySQL `root` sin contraseña | [Ver](../machines/starting-point/sequel/README.md) | [EN](../machines/starting-point/sequel/README.en.md) |
| Appointment | Linux | Very Easy | SQLi en login `admin' or '1'='1'#` | [Ver](../machines/starting-point/appointment/README.md) | [EN](../machines/starting-point/appointment/README.en.md) |
| Crocodile | Linux | Very Easy | FTP anónimo con listas de usuarios | [Ver](../machines/starting-point/crocodile/README.md) | [EN](../machines/starting-point/crocodile/README.en.md) |
| Responder | Windows | Very Easy | LFI a UNC, NetNTLMv2 y WinRM | [Ver](../machines/starting-point/responder/README.md) | [EN](../machines/starting-point/responder/README.en.md) |
| Three | Linux | Very Easy | Bucket S3 sin IAM y webshell | [Ver](../machines/starting-point/three/README.md) | [EN](../machines/starting-point/three/README.en.md) |
| Ignition | Linux | Very Easy | Magento con `admin:qwerty123` | [Ver](../machines/starting-point/ignition/README.md) | [EN](../machines/starting-point/ignition/README.en.md) |
| Bike | Linux | Very Easy | SSTI de Handlebars como root | [Ver](../machines/starting-point/bike/README.md) | [EN](../machines/starting-point/bike/README.en.md) |
| Funnel | Linux | Very Easy | Spray SSH y túnel a PostgreSQL | [Ver](../machines/starting-point/funnel/README.md) | [EN](../machines/starting-point/funnel/README.en.md) |
| Pennyworth | Linux | Very Easy | Jenkins `root:password` y Groovy | [Ver](../machines/starting-point/pennyworth/README.md) | [EN](../machines/starting-point/pennyworth/README.en.md) |
| Tactics | Windows | Very Easy | SMB nulo y `Administrator` vacío | [Ver](../machines/starting-point/tactics/README.md) | [EN](../machines/starting-point/tactics/README.en.md) |
| Archetype | Windows | Very Easy | `prod.dtsConfig`, `xp_cmdshell`, psexec | [Ver](../machines/starting-point/archetype/README.md) | [EN](../machines/starting-point/archetype/README.en.md) |
| Oopsie | Linux | Very Easy | IDOR en cookies, subida y SUID | [Ver](../machines/starting-point/oopsie/README.md) | [EN](../machines/starting-point/oopsie/README.en.md) |
| Vaccine | Linux | Very Easy | `backup.zip`, SQLi y `sudo vi` | [Ver](../machines/starting-point/vaccine/README.md) | [EN](../machines/starting-point/vaccine/README.en.md) |
| Unified | Linux | Very Easy | Log4Shell en UniFi y MongoDB | [Ver](../machines/starting-point/unified/README.md) | [EN](../machines/starting-point/unified/README.en.md) |
| Included | Linux | Very Easy | LFI, TFTP y grupo `lxd` | [Ver](../machines/starting-point/included/README.md) | [EN](../machines/starting-point/included/README.en.md) |
| Markup | Windows | Very Easy | XXE a `id_rsa` y `job.bat` | [Ver](../machines/starting-point/markup/README.md) | [EN](../machines/starting-point/markup/README.en.md) |
| Base | Linux | Very Easy | `strcmp` con arrays y `sudo find` | [Ver](../machines/starting-point/base/README.md) | [EN](../machines/starting-point/base/README.en.md) |
