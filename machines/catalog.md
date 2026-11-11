# Catálogo de máquinas retiradas

[🇬🇧 English](catalog.en.md) | **Español**

Fichas de máquinas que sirven para estudiar técnicas. La tabla principal reúne las **retiradas**; al final hay una sección con las 25 de **Starting Point**, que siguen disponibles en la plataforma. Las marcadas como `ref.` no se han jugado en este perfil: son material de estudio, no un logro, y no llevan flags ni credenciales. Las que sí están jugadas viven en `machines/linux/`, `machines/windows/` o `machines/starting-point/` y aparecen en el índice principal.

## Escritas

| Máquina | OS | Dificultad | Técnica principal | ES | EN |
|---|---|---|---|---|---|
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

Estas 25 máquinas no están retiradas —siguen disponibles en la plataforma— pero se catalogan aquí para que el índice cubra las 116 fichas del repositorio. El detalle, con tier y servicio, está en el índice de la sección.

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
