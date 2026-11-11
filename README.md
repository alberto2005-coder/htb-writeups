# 🎯 HTB Writeups — alberto2005coder

**Español** | [🇬🇧 English](README.en.md)

Repositorio personal de writeups, notas y metodología de **Hack The Box**.

> **Estado:** borradores en construcción. Las máquinas **activas** no se publican hasta que HTB las retire.
>
> **Cifras:** 116 máquinas, 58 Sherlocks, 79 retos y 64 temas de conocimiento, cada uno en ES/EN.

---

## 👤 Perfil

- **HTB:** [alberto2005coder](https://app.hackthebox.com/users/4187928)
- **Enfoque:** pentesting web, Linux, Active Directory y cloud.
- **Objetivo:** documentar el proceso completo (reconocimiento → foothold → escalada → mitigación), no solo el comando final.

---

## 🗂️ Máquinas

| Máquina | OS | Dificultad | Categoría | Estado | Técnicas clave | ES | EN |
|---|---|---|---|---|---|---|---|
| Meow | Linux | Very Easy | Starting Point | **Available** | FTP/Telnet sin credenciales | [Ver](machines/starting-point/meow/README.md) | [EN](machines/starting-point/meow/README.en.md) |
| Fawn | Linux | Very Easy | Starting Point | **Available** | FTP anónimo | [Ver](machines/starting-point/fawn/README.md) | [EN](machines/starting-point/fawn/README.en.md) |
| Dancing | Windows | Very Easy | Starting Point | **Available** | SMB null session | [Ver](machines/starting-point/dancing/README.md) | [EN](machines/starting-point/dancing/README.en.md) |
| Redeemer | Linux | Very Easy | Starting Point | **Available** | Redis sin autenticación | [Ver](machines/starting-point/redeemer/README.md) | [EN](machines/starting-point/redeemer/README.en.md) |
| Nibbles | Linux | Easy | CMS / Web | **Retired** (ref.) | Nibbleblog 4.0.3, subida CVE-2015-6967, sudo | [Ver](machines/linux/nibbles/README.md) | [EN](machines/linux/nibbles/README.en.md) |
| Doctor | Linux | Easy | Web / Infraestructura | **Retired** (ref.) | SSTI con Jinja2 en un vhost, Splunk 8.0.x | [Ver](machines/linux/doctor/README.md) | [EN](machines/linux/doctor/README.en.md) |
| Poison | FreeBSD | Medium | Web / Unix | **Retired** (ref.) | LFI en `browse.php`, base64 en `pwdbackup.txt`, VNC como root con `secret.zip` | [Ver](machines/freebsd/poison/README.md) | [EN](machines/freebsd/poison/README.en.md) |
| SolidState | Linux | Medium | Servicios | **Retired** (ref.) | Apache James con credenciales por defecto, cron escribible | [Ver](machines/linux/solidstate/README.md) | [EN](machines/linux/solidstate/README.en.md) |
| DevOops | Linux | Medium | Web / Desarrollo | **Retired** (ref.) | XXE en la subida de XML y clave de root en el historial de git | [Ver](machines/linux/devoops/README.md) | [EN](machines/linux/devoops/README.en.md) |
| Pirate | Windows | Hard | Active Directory | **Retired** (ref.) | Pre-Windows 2000, gMSA, RBCD, S4U2Proxy | [Ver](machines/windows/pirate/README.md) | [EN](machines/windows/pirate/README.en.md) |
| MonitorsFour | Windows | Easy | Web / Contenedores | **Retired** (ref.) | IDOR en la API, MD5 crackeado, CVE-2025-24367 en Cacti, escape por la API de Docker | [Ver](machines/windows/monitorsfour/README.md) | [EN](machines/windows/monitorsfour/README.en.md) |
| Pterodactyl | Linux | Medium | Web / Linux | **Retired** (ref.) | CVE-2025-49132 en `/locales`, PEAR `pearcmd`, cadena CVE-2025-6018/6019 | [Ver](machines/linux/pterodactyl/README.md) | [EN](machines/linux/pterodactyl/README.en.md) |
| Frolic | Linux | Easy | Web / Linux | **Retired** (ref.) | Login validado en JS, PlaySMS 1.4 con subida de CSV y SUID `rop` con ret2libc | [Ver](machines/linux/frolic/README.md) | [EN](machines/linux/frolic/README.en.md) |
| Sea | Linux | Easy | Web / Linux | **Retired** (ref.) | WonderCMS CVE-2023-41425, hash bcrypt crackeado e inyección de comandos en el 8080 | [Ver](machines/linux/sea/README.md) | [EN](machines/linux/sea/README.en.md) |
| Devel | Windows | Easy | Windows / Web | **Retired** (ref.) | FTP anónimo escribible sobre IIS, webshell ASPX y MS10-015 o `SeImpersonate` | [Ver](machines/windows/devel/README.md) | [EN](machines/windows/devel/README.en.md) |
| Fluffy | Windows | Easy | Active Directory | **Retired** (ref.) | CVE-2025-24071 para robar NTLM, shadow credentials y ADCS ESC16 | [Ver](machines/windows/fluffy/README.md) | [EN](machines/windows/fluffy/README.en.md) |
| Garfield | Windows | Hard | Active Directory | **Retired** (ref.) | RODC, ticket dorado con KeyList, volcado del DC y pass-the-hash | [Ver](machines/windows/garfield/README.md) | [EN](machines/windows/garfield/README.en.md) |
| Buff | Windows | Easy | Web | **Retired** (ref.) | Subida sin autenticacion, CloudMe 1.11.2 | [Ver](machines/windows/buff/README.md) | [EN](machines/windows/buff/README.en.md) |
| Blackfield | Windows | Hard | Active Directory | **Retired** (ref.) | AS-REP, volcado de lsass, SeBackupPrivilege, NTDS | [Ver](machines/windows/blackfield/README.md) | [EN](machines/windows/blackfield/README.en.md) |
| Explosion | Windows | Very Easy | Starting Point | **Available** | RDP con la cuenta `Administrator` sin contraseña | [Ver](machines/starting-point/explosion/README.md) | [EN](machines/starting-point/explosion/README.en.md) |
| Preignition | Linux | Very Easy | Starting Point | **Available** | Panel `/admin.php` oculto con `admin:admin` | [Ver](machines/starting-point/preignition/README.md) | [EN](machines/starting-point/preignition/README.en.md) |
| Mongod | Linux | Very Easy | Starting Point | **Available** | MongoDB en 27017 sin autenticación | [Ver](machines/starting-point/mongod/README.md) | [EN](machines/starting-point/mongod/README.en.md) |
| Synced | Linux | Very Easy | Starting Point | **Available** | rsync anónimo en 873 | [Ver](machines/starting-point/synced/README.md) | [EN](machines/starting-point/synced/README.en.md) |
| Sequel | Linux | Very Easy | Starting Point | **Available** | MySQL con `root` sin contraseña | [Ver](machines/starting-point/sequel/README.md) | [EN](machines/starting-point/sequel/README.en.md) |
| Appointment | Linux | Very Easy | Starting Point | **Available** | SQLi en el login: `admin' or '1'='1'#` | [Ver](machines/starting-point/appointment/README.md) | [EN](machines/starting-point/appointment/README.en.md) |
| Crocodile | Linux | Very Easy | Starting Point | **Available** | FTP anónimo con `allowed.userlist` y `.passwd` | [Ver](machines/starting-point/crocodile/README.md) | [EN](machines/starting-point/crocodile/README.en.md) |
| Responder | Windows | Very Easy | Starting Point | **Available** | LFI a UNC, captura NetNTLMv2 y WinRM | [Ver](machines/starting-point/responder/README.md) | [EN](machines/starting-point/responder/README.en.md) |
| Three | Linux | Very Easy | Starting Point | **Available** | Bucket S3 sin autenticación y webshell | [Ver](machines/starting-point/three/README.md) | [EN](machines/starting-point/three/README.en.md) |
| Ignition | Linux | Very Easy | Starting Point | **Available** | Magento con `admin:qwerty123` en `/admin` | [Ver](machines/starting-point/ignition/README.md) | [EN](machines/starting-point/ignition/README.en.md) |
| Bike | Linux | Very Easy | Starting Point | **Available** | SSTI de Handlebars en Node.js hasta root | [Ver](machines/starting-point/bike/README.md) | [EN](machines/starting-point/bike/README.en.md) |
| Funnel | Linux | Very Easy | Starting Point | **Available** | Spray SSH y túnel al PostgreSQL en loopback | [Ver](machines/starting-point/funnel/README.md) | [EN](machines/starting-point/funnel/README.en.md) |
| Pennyworth | Linux | Very Easy | Starting Point | **Available** | Jenkins `root:password` y consola Groovy | [Ver](machines/starting-point/pennyworth/README.md) | [EN](machines/starting-point/pennyworth/README.en.md) |
| Tactics | Windows | Very Easy | Starting Point | **Available** | Sesión nula SMB y `Administrator` sin contraseña | [Ver](machines/starting-point/tactics/README.md) | [EN](machines/starting-point/tactics/README.en.md) |
| Archetype | Windows | Very Easy | Starting Point | **Available** | `prod.dtsConfig`, `xp_cmdshell`, historial PS y psexec | [Ver](machines/starting-point/archetype/README.md) | [EN](machines/starting-point/archetype/README.en.md) |
| Oopsie | Linux | Very Easy | Starting Point | **Available** | IDOR en cookies, subida de webshell y SUID `bugtracker` | [Ver](machines/starting-point/oopsie/README.md) | [EN](machines/starting-point/oopsie/README.en.md) |
| Vaccine | Linux | Very Easy | Starting Point | **Available** | `backup.zip`, SQLi con `sqlmap --os-shell` y `sudo vi` | [Ver](machines/starting-point/vaccine/README.md) | [EN](machines/starting-point/vaccine/README.en.md) |
| Unified | Linux | Very Easy | Starting Point | **Available** | Log4Shell (CVE-2021-44228) en UniFi y MongoDB 27117 | [Ver](machines/starting-point/unified/README.md) | [EN](machines/starting-point/unified/README.en.md) |
| Included | Linux | Very Easy | Starting Point | **Available** | LFI a `/proc/net/udp`, TFTP sin auth y grupo `lxd` | [Ver](machines/starting-point/included/README.md) | [EN](machines/starting-point/included/README.en.md) |
| Markup | Windows | Very Easy | Starting Point | **Available** | XXE para leer `id_rsa` y `job.bat` programado | [Ver](machines/starting-point/markup/README.md) | [EN](machines/starting-point/markup/README.en.md) |
| Base | Linux | Very Easy | Starting Point | **Available** | `strcmp` con arrays, subida sin filtro y `sudo find` | [Ver](machines/starting-point/base/README.md) | [EN](machines/starting-point/base/README.en.md) |
| Cap | Linux | Easy | Machines | **Retired** | IDOR, análisis de pcap, `cap_setuid` | [Ver](machines/linux/cap/README.md) | [EN](machines/linux/cap/README.en.md) |
| MakeSense | Linux | Medium | Season 11 | **Retired** | XSS al bot admin, AES-GCM forjado, plugin malicioso, OCR como root | [Ver](machines/linux/makesense/README.md) | [EN](machines/linux/makesense/README.en.md) |
| DutyBound | Linux | Medium | Season 12 | **Active** | BCBP, SQLi en PostgreSQL, `COPY TO PROGRAM`, X11/XTEST, path unit con `eval` | [Borrador](machines/active/dutybound/README.md) | [EN](machines/active/dutybound/README.en.md) |
| Stream | Linux | Medium | Season 12 | **Active** | Heapdump, XXE, ClickHouse, Kopia, timer root | [Borrador](machines/active/stream/README.md) | [EN](machines/active/stream/README.en.md) |
| Layover | Linux | Medium | Season 12 | **Active** | Credenciales WiFi en texto claro, utilidades del CP de Craft (backup de BD + phpinfo), descifrado Yii, CUPS 2.4.16 CVE-2026-34990 | [Borrador](machines/active/layover/README.md) | [EN](machines/active/layover/README.en.md) |
| Connected | Linux | Easy | Season 11 | **Active** | FreePBX 16: SQLi apilada CVE-2025-57819 + path traversal CVE-2025-61678 hasta webshell, e incron con `init.conf` sourced como root | [Borrador](machines/active/connected/README.md) | [EN](machines/active/connected/README.en.md) |
| Unclaimed | Windows | Medium | Season 12 | **Active** | Chatbot con SQL: `IMPERSONATE` a sysadmin, `xp_cmdshell`, descifrado DPAPI de un credential, y `SeBackupPrivilege` con `robocopy /B` | [Borrador](machines/active/unclaimed/README.md) | [EN](machines/active/unclaimed/README.en.md) |
| Armageddon | Linux | Easy | Machines | **Retired** (ref.) | Drupal 7.56, Drupalgeddon2, hook de snap con `sudo` | [Ver](machines/linux/armageddon/README.md) | [EN](machines/linux/armageddon/README.en.md) |
| Bashed | Linux | Easy | Machines | **Retired** (ref.) | webshell `phpbash`, `sudo -u scriptmanager`, cron de root | [Ver](machines/linux/bashed/README.md) | [EN](machines/linux/bashed/README.en.md) |
| Bastion | Windows | Easy | Machines | **Retired** (ref.) | backup SMB con VHDX, SAM/SYSTEM, mRemoteNG | [Ver](machines/windows/bastion/README.md) | [EN](machines/windows/bastion/README.en.md) |
| Beep | Linux | Easy | Machines | **Retired** (ref.) | LFI en Elastix, CVE-2012-4869, `nmap` interactivo | [Ver](machines/linux/beep/README.md) | [EN](machines/linux/beep/README.en.md) |
| Blocky | Linux | Easy | Machines | **Retired** (ref.) | credenciales en un JAR, reutilización, `sudo ALL` | [Ver](machines/linux/blocky/README.md) | [EN](machines/linux/blocky/README.en.md) |
| Blunder | Linux | Easy | Machines | **Retired** (ref.) | Bludit, bypass de fuerza bruta, `sudo -u#-1` | [Ver](machines/linux/blunder/README.md) | [EN](machines/linux/blunder/README.en.md) |
| Bounty | Windows | Easy | Machines | **Retired** (ref.) | `web.config` en IIS, `SeImpersonate`, JuicyPotato | [Ver](machines/windows/bounty/README.md) | [EN](machines/windows/bounty/README.en.md) |
| Delivery | Linux | Easy | Machines | **Retired** (ref.) | osTicket + Mattermost, bcrypt con reglas | [Ver](machines/linux/delivery/README.md) | [EN](machines/linux/delivery/README.en.md) |
| Facts | Linux | Easy | Machines | **Retired** (ref.) | Camaleon CMS, MinIO, clave SSH, `facter` | [Ver](machines/linux/facts/README.md) | [EN](machines/linux/facts/README.en.md) |
| Forest | Windows | Easy | Machines | **Retired** (ref.) | AS-REP, `Account Operators` a Exchange, DCSync | [Ver](machines/windows/forest/README.md) | [EN](machines/windows/forest/README.en.md) |
| FriendZone | Linux | Easy | Machines | **Retired** (ref.) | AXFR, LFI + SMB, hijack de `os.py` | [Ver](machines/linux/friendzone/README.md) | [EN](machines/linux/friendzone/README.en.md) |
| Admirer | Linux | Easy | Machines | **Retired** (ref.) | Adminer 4.6.2 con MySQL propio y `PYTHONPATH` heredado por sudo | [Ver](machines/linux/admirer/README.md) | [EN](machines/linux/admirer/README.en.md) |
| Arctic | Windows | Easy | Machines | **Retired** (ref.) | ColdFusion 8 + FCKeditor, `SeImpersonate`, JuicyPotato | [Ver](machines/windows/arctic/README.md) | [EN](machines/windows/arctic/README.en.md) |
| Bank | Linux | Easy | Machines | **Retired** (ref.) | AXFR, `302` a `200`, whitelist `.htb`, SUID `emergency` | [Ver](machines/linux/bank/README.md) | [EN](machines/linux/bank/README.en.md) |
| Blue | Windows | Easy | Machines | **Retired** (ref.) | MS17-010 EternalBlue, `hashdump` | [Ver](machines/windows/blue/README.md) | [EN](machines/windows/blue/README.en.md) |
| Cronos | Linux | Medium | Machines | **Retired** (ref.) | AXFR, SQLi, inyección de comandos, cron de root sobre `artisan` | [Ver](machines/linux/cronos/README.md) | [EN](machines/linux/cronos/README.en.md) |
| PingPong | Windows | Insane | Machines | **Retired** | Dos bosques AD, ESC13, pivote, gMSA, JEA, RBCD y ESC4→ESC1 | [Ver](machines/windows/pingpong/README.md) | [EN](machines/windows/pingpong/README.en.md) |
| AirTouch | Linux | Medium | Machines | **Retired** (ref.) | Handshake WPA2, Evil Twin PEAP-MSCHAPv2 y pivote por VPN | [Ver](machines/linux/airtouch/README.md) | [EN](machines/linux/airtouch/README.en.md) |
| Eighteen | Windows | Hard | Machines | **Retired** (ref.) | `IMPERSONATE` en MSSQL, hash Werkzeug, CVE-2025-53779 (dMSA) | [Ver](machines/windows/eighteen/README.md) | [EN](machines/windows/eighteen/README.en.md) |
| Sink | Linux | Insane | Machines | **Retired** (ref.) | Smuggling CL.TE, Gitea con claves AWS, Secrets Manager y KMS | [Ver](machines/linux/sink/README.md) | [EN](machines/linux/sink/README.en.md) |
| Sorcery | Linux | Insane | Machines | **Retired** (ref.) | Cypher injection, XSS en passkeys, Kafka y FreeIPA | [Ver](machines/linux/sorcery/README.md) | [EN](machines/linux/sorcery/README.en.md) |
| Cobblestone | Linux | Insane | Machines | **Retired** (ref.) | SQLi de segundo orden, XSS, Twig SSTI y CVE-2024-47533 | [Ver](machines/linux/cobblestone/README.md) | [EN](machines/linux/cobblestone/README.en.md) |
| Code | Linux | Easy | Machines | **Retired** (ref.) | Escape de blocklist en Python, bcrypt y `backy.sh` con traversal | [Ver](machines/linux/code/README.md) | [EN](machines/linux/code/README.en.md) |
| Kobold | Linux | Easy | Machines | **Retired** (ref.) | MCPJam Inspector CVE-2026-23744, PrivateBin y contenedor privilegiado | [Ver](machines/linux/kobold/README.md) | [EN](machines/linux/kobold/README.en.md) |
| Helix | Linux | Medium | Machines | **Retired** (ref.) | NiFi 1.21.0, `CREATE ALIAS` de H2 (CVE-2023-34468) y OPC UA | [Ver](machines/linux/helix/README.md) | [EN](machines/linux/helix/README.en.md) |
| Interpreter | Linux | Medium | Machines | **Retired** (ref.) | Mirth Connect CVE-2023-43208, PBKDF2 y `eval()` en servicio local | [Ver](machines/linux/interpreter/README.md) | [EN](machines/linux/interpreter/README.en.md) |
| VariaType | Linux | Medium | Machines | **Retired** (ref.) | fontTools CVE-2025-66034, FontForge CVE-2024-25082 y setuptools CVE-2025-47273 | [Ver](machines/linux/variatype/README.md) | [EN](machines/linux/variatype/README.en.md) |
| Academy | Linux | Easy | Web / Linux | **Retired** (ref.) | Roleid → Laravel CVE-2018-15133 con `APP_KEY`, `.env` y `composer` por sudo | [Ver](machines/linux/academy/README.md) | [EN](machines/linux/academy/README.en.md) |
| Active | Windows | Easy | Active Directory | **Retired** (ref.) | GPP en SYSVOL, `gpp-decrypt`, Kerberoasting a `Administrator` | [Ver](machines/windows/active/README.md) | [EN](machines/windows/active/README.en.md) |
| Apocalyst | Linux | Medium | Web / Linux | **Retired** (ref.) | WordPress, `cewl` y `steghide`, hydra, plugin PHP y `/etc/passwd` escribible | [Ver](machines/linux/apocalyst/README.md) | [EN](machines/linux/apocalyst/README.en.md) |
| OpenAdmin | Linux | Easy | Web / Linux | **Retired** (ref.) | OpenNetAdmin 18.1.1, reutilización de credenciales, `ssh2john` y escape de `nano` | [Ver](machines/linux/openadmin/README.md) | [EN](machines/linux/openadmin/README.en.md) |
| Tabby | Linux | Easy | Web / Linux | **Retired** (ref.) | LFI a `tomcat-users.xml`, WAR por `manager/text`, `fcrackzip` y grupo `lxd` | [Ver](machines/linux/tabby/README.md) | [EN](machines/linux/tabby/README.en.md) |
| Jerry | Windows | Easy | Web / Windows | **Retired** (ref.) | Tomcat 7 con credenciales por defecto, WAR por `/manager/text` y shell directa como SYSTEM | [Ver](machines/windows/jerry/README.md) | [EN](machines/windows/jerry/README.en.md) |
| Chatterbox | Windows | Medium | Servicios / Windows | **Retired** (ref.) | Desbordamiento en AChat 0.150 (EDB 36025) y AutoLogon en el registro | [Ver](machines/windows/chatterbox/README.md) | [EN](machines/windows/chatterbox/README.en.md) |
| Heist | Windows | Easy | Web / Windows | **Retired** (ref.) | Config de Cisco con type 7 y type 5, spray a WinRM y `procdump` sobre Firefox | [Ver](machines/windows/heist/README.md) | [EN](machines/windows/heist/README.en.md) |
| Valentine | Linux | Easy | Web / Linux | **Retired** (ref.) | Heartbleed filtra la passphrase de una clave RSA, SSH y socket de `tmux` de root | [Ver](machines/linux/valentine/README.md) | [EN](machines/linux/valentine/README.en.md) |
| Shocker | Linux | Easy | Web / Linux | **Retired** (ref.) | Shellshock en un CGI (`user.sh`) y `sudo perl` de GTFOBins | [Ver](machines/linux/shocker/README.md) | [EN](machines/linux/shocker/README.en.md) |
| SwagShop | Linux | Easy | Web / Linux | **Retired** (ref.) | Magento con SQLi Shoplift, Connect Manager y `sudo vi` | [Ver](machines/linux/swagshop/README.md) | [EN](machines/linux/swagshop/README.en.md) |
| Networked | Linux | Easy | Web / Linux | **Retired** (ref.) | Backup con el código, doble extensión, cron inyectable y `changename.sh` que `source`a el ifcfg | [Ver](machines/linux/networked/README.md) | [EN](machines/linux/networked/README.en.md) |
| Sense | FreeBSD | Easy | Infraestructura / FreeBSD | **Retired** (ref.) | pfSense 2.1.3 con credenciales por defecto y CVE-2014-4688 como root | [Ver](machines/freebsd/sense/README.md) | [EN](machines/freebsd/sense/README.en.md) |
| Legacy | Windows | Easy | Windows / SMB | **Retired** (ref.) | MS08-067 sobre SMBv1 en Windows XP | [Ver](machines/windows/legacy/README.md) | [EN](machines/windows/legacy/README.en.md) |
| Sunday | Solaris | Easy | Servicios / Solaris | **Retired** (ref.) | `finger` para enumerar usuarios, shadow crackeado y `sudo wget` | [Ver](machines/solaris/sunday/README.md) | [EN](machines/solaris/sunday/README.en.md) |
| Lame | Linux | Easy | SMB / servicios antiguos | **Retired** (ref.) | Samba `usermap_script` (CVE-2007-2447) para root directo; `distcc` y `vsftpd` como alternativas | [Ver](machines/linux/lame/README.md) | [EN](machines/linux/lame/README.en.md) |
| Optimum | Windows | Easy | Web / Windows | **Retired** (ref.) | Rejetto HFS 2.3 (CVE-2014-6287) y MS16-032 hasta SYSTEM | [Ver](machines/windows/optimum/README.md) | [EN](machines/windows/optimum/README.en.md) |
| Sau | Linux | Easy | Web / SSRF | **Retired** (ref.) | SSRF en Request Baskets hacia Maltrail y `sudo systemctl` con escape del pager | [Ver](machines/linux/sau/README.md) | [EN](machines/linux/sau/README.en.md) |
| Nineveh | Linux | Medium | Web / Enumeración | **Retired** (ref.) | phpLiteAdmin + LFI, port knocking y chkrootkit 0.49 como root | [Ver](machines/linux/nineveh/README.md) | [EN](machines/linux/nineveh/README.en.md) |
| Jeeves | Windows | Medium | Windows / Credenciales | **Retired** (ref.) | Jenkins sin autenticación, KeePass, pass-the-hash y flag en un flujo NTFS | [Ver](machines/windows/jeeves/README.md) | [EN](machines/windows/jeeves/README.en.md) |
| CozyHosting | Linux | Easy | Web / Spring Boot | **Retired** (ref.) | Actuator que filtra sesiones, inyección de comandos en el panel, PostgreSQL y `sudo ssh` | [Ver](machines/linux/cozyhosting/README.md) | [EN](machines/linux/cozyhosting/README.en.md) |
| BoardLight | Linux | Easy | Web / CMS | **Retired** (ref.) | Dolibarr 17.0.0 con credenciales por defecto, CVE-2023-30253 y SUID de Enlightenment | [Ver](machines/linux/boardlight/README.md) | [EN](machines/linux/boardlight/README.en.md) |
| Busqueda | Linux | Easy | Web / Inyección | **Retired** (ref.) | `eval()` de Searchor, `.git` con credenciales, Gitea y `full-checkup.sh` relativo | [Ver](machines/linux/busqueda/README.md) | [EN](machines/linux/busqueda/README.en.md) |
| Soccer | Linux | Easy | Web / SQLi en WebSocket | **Retired** (ref.) | Tiny File Manager por defecto, SQLi ciega por WebSocket y `doas` con `dstat` | [Ver](machines/linux/soccer/README.md) | [EN](machines/linux/soccer/README.en.md) |
| Timelapse | Windows | Easy | Active Directory / Certificados | **Retired** (ref.) | SMB anónimo, PFX, historial de PowerShell y LAPS hasta Administrator | [Ver](machines/windows/timelapse/README.md) | [EN](machines/windows/timelapse/README.en.md) |
| Cicada | Windows | Easy | Active Directory / SMB | **Retired** (ref.) | SMB de invitado, contraseña de onboarding, spray, `description` e `info`, `SeBackupPrivilege` y SAM/SYSTEM | [Ver](machines/windows/cicada/README.md) | [EN](machines/windows/cicada/README.en.md) |
| Support | Windows | Easy | Active Directory | **Retired** (ref.) | Reversing de `UserInfo.exe` (XOR + base64), LDAP, contraseña en `info`, GenericAll sobre el DC y RBCD | [Ver](machines/windows/support/README.md) | [EN](machines/windows/support/README.en.md) |
| Administrator | Windows | Medium | Active Directory | **Retired** (ref.) | GenericAll y ForceChangePassword, FTP con `.psafe3`, GenericWrite, targeted kerberoasting y DCSync | [Ver](machines/windows/administrator/README.md) | [EN](machines/windows/administrator/README.en.md) |
| Escape | Windows | Medium | Active Directory / MSSQL | **Retired** (ref.) | PDF con credenciales, `xp_dirtree` como `sql_svc`, `ERRORLOG.BAK` y ADCS ESC1 hasta Administrator | [Ver](machines/windows/escape/README.md) | [EN](machines/windows/escape/README.en.md) |
| Pilgrimage | Linux | Easy | Web / Linux | **Retired** (ref.) | `/.git` expuesto, ImageMagick 7.1.0-49 (CVE-2022-44268) y binwalk 2.3.2 (CVE-2022-4510) | [Ver](machines/linux/pilgrimage/README.md) | [EN](machines/linux/pilgrimage/README.en.md) |
| Sauna | Windows | Easy | Active Directory | **Retired** (ref.) | AS-REP roasting, credenciales de autologon y DCSync | [Ver](machines/windows/sauna/README.md) | [EN](machines/windows/sauna/README.en.md) |
| Netmon | Windows | Easy | Web / Windows | **Retired** (ref.) | FTP anónimo, PRTG y CVE-2018-9276 | [Ver](machines/windows/netmon/README.md) | [EN](machines/windows/netmon/README.en.md) |
| Servmon | Windows | Easy | Windows / Servicios | **Retired** (ref.) | NVMS path traversal, NSClient++ y túnel SSH | [Ver](machines/windows/servmon/README.md) | [EN](machines/windows/servmon/README.en.md) |
| Resolute | Windows | Medium | Active Directory | **Retired** (ref.) | LDAP anónimo, reutilización y `DnsAdmins` | [Ver](machines/windows/resolute/README.md) | [EN](machines/windows/resolute/README.en.md) |
| Bastard | Windows | Medium | Web / Windows | **Retired** (ref.) | Drupalgeddon2 y JuicyPotato | [Ver](machines/windows/bastard/README.md) | [EN](machines/windows/bastard/README.en.md) |
| Cascade | Windows | Medium | Active Directory / Windows | **Retired** (ref.) | LDAP anónimo, `cascadeLegacyPwd`, VNC reversible y AD Recycle Bin | [Ver](machines/windows/cascade/README.md) | [EN](machines/windows/cascade/README.en.md) |
| Traceback | Linux | Easy | Web / Linux | **Retired** (ref.) | Webshell SmEvK con credenciales por defecto, `luvit` por sudo y MOTD escribible | [Ver](machines/linux/traceback/README.md) | [EN](machines/linux/traceback/README.en.md) |
| Craft | Linux | Easy | Web / Linux | **Retired** (ref.) | `eval()` en Flask, historial de Gogs, MySQL en claro y OTP de Vault | [Ver](machines/linux/craft/README.md) | [EN](machines/linux/craft/README.en.md) |
| Book | Linux | Medium | Web / Linux | **Retired** (ref.) | Truncado SQL en el registro, XSS en el PDF y carrera de `logrotate` | [Ver](machines/linux/book/README.md) | [EN](machines/linux/book/README.en.md) |
| Querier | Windows | Medium | Active Directory / MSSQL | **Retired** (ref.) | Macro con credenciales, `xp_dirtree`, NetNTLMv2 y GPP | [Ver](machines/windows/querier/README.md) | [EN](machines/windows/querier/README.en.md) |
| Remote | Windows | Medium | Web / Windows | **Retired** (ref.) | NFS con el backup de Umbraco, SHA1, RCE XSLT y TeamViewer | [Ver](machines/windows/remote/README.md) | [EN](machines/windows/remote/README.en.md) |
| Luke | FreeBSD | Medium | Web / FreeBSD | **Retired** (ref.) | `config.php` en claro, API con JWT y Ajenti como root | [Ver](machines/freebsd/luke/README.md) | [EN](machines/freebsd/luke/README.en.md) |

> **Estados:** **Available** = Starting Point, siempre disponible y publicable · **Retired** = retirada, publicable · **Active** = en su temporada, no se publica hasta que HTB la retire · **ref.** = ficha de referencia, no jugada en este perfil.
>
> Catálogo de fichas de referencia: [machines/catalog.md](machines/catalog.md) · [EN](machines/catalog.en.md).

### 🏅 Logros verificables

Las máquinas completadas en este perfil tienen aquí su enlace público. Las fichas marcadas como `ref.` no aparecen: son material de estudio y no hay un logro propio que enlazar.

| Máquina | Logro |
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

- **Retired:** writeup publicable.
- **Active:** solo borrador privado; se publica cuando HTB retire la máquina.

---

## 🧩 Retos

Retos resueltos. No hay escalada: el objetivo es la flag del reto, así que el writeup se centra en el fallo y en la cadena de explotación.

| Reto | Tipo | Dificultad | Estado | Técnicas clave | ES | EN |
|---|---|---|---|---|---|---|
| Kryptor | Pwn | Insane | **Retired** | DirtyPipe (CVE-2022-0847) en kernel 5.9.10: busybox parcheado en page cache y `modprobe` como root | [Ver](challenges/Kryptor/README.md) | [EN](challenges/Kryptor/README.en.md) |
| Oldbridge | Pwn | Medium | **Retired** | BOF con XOR `0xd`: canario heredado por `fork`, base de PIE y stack pivot a ROP | [Ver](challenges/Oldbridge/README.md) | [EN](challenges/Oldbridge/README.en.md) |
| Space Pirate: Entrypoint | Pwn | Very Easy | **Retired** | Format string: `%7$hn` escribe `0x1337` en la variable que abre la puerta | [Ver](challenges/Space%20Pirate%20Entrypoint/README.md) | [EN](challenges/Space%20Pirate%20Entrypoint/README.en.md) |
| Space Pirate: Going Deeper | Pwn | Very Easy | **Retired** | `read` de 57 en un búfer de 40; sobrescritura parcial del retorno a `0x400b01` | [Ver](challenges/Space%20Pirate%20Going%20Deeper/README.md) | [EN](challenges/Space%20Pirate%20Going%20Deeper/README.en.md) |
| Vault-breaker | Pwn | Very Easy | **Retired** | Clave generada de 31 a 0 bytes: `strcpy` la vacía y el XOR revela la flag | [Ver](challenges/Vault-breaker/README.md) | [EN](challenges/Vault-breaker/README.en.md) |
| Dark Embargo | Web / Pwn | Medium | **Retired** | PHP 8.4.26: OOM en `session.upload_progress` → use-after-free (CVE-2026-109618/109619), leak de ASLR por `Set-Cookie` y `pDestructor` → `system()` | [Ver](challenges/Dark%20Embargo/README.md) | [EN](challenges/Dark%20Embargo/README.en.md) |
| Emdee five for life | Misc | Very Easy | **Retired** | MD5 contra reloj: sesión HTTP, regex y automatización | [Ver](challenges/Emdee%20five%20for%20life/README.md) | [EN](challenges/Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | **Retired** | Inyección LDAP en login y buscador (`*` como comodín) | [Ver](challenges/Phonebook/README.md) | [EN](challenges/Phonebook/README.en.md) |
| Under Construction | Web | Easy | **Retired** | Confusión de algoritmos JWT: firmar HS256 con la clave pública | [Ver](challenges/Under%20Construction/README.md) | [EN](challenges/Under%20Construction/README.en.md) |
| Gunship | Web | Easy | **Retired** | Prototype pollution en `flat@5.0.0` y AST injection en el motor de plantillas (variantes Handlebars y Pug) | [Ver](challenges/Gunship/README.md) | [EN](challenges/Gunship/README.en.md) |
| baby interdimensional internet | Web | Easy | **Retired** | `exec()` de Python 2 sobre `ingredient`/`measurements`, sin filtros ni límites | [Ver](challenges/baby%20interdimensional%20internet/README.md) | [EN](challenges/baby%20interdimensional%20internet/README.en.md) |
| Interdimensional Internet | Web | Medium | **Retired** | WAF de `[ ( _ .` evadido con `\x5b\x28\x5f\x2e` y exfiltración por `flask.session` | [Ver](challenges/Interdimensional%20Internet/README.md) | [EN](challenges/Interdimensional%20Internet/README.en.md) |
| Fake Boost | Forensics | Easy | **Retired** | PowerShell invertido + base64, AES-CBC y exfiltración HTTP a un `POST` | [Ver](challenges/Fake%20Boost/README.md) | [EN](challenges/Fake%20Boost/README.en.md) |
| Impossible Password | Reversing | Easy | **Retired** | Segundo `strcmp` contra `rand()`: igualar `$rdi`/`$rsi` en gdb | [Ver](challenges/Impossible%20Password/README.md) | [EN](challenges/Impossible%20Password/README.en.md) |
| Reg | Pwn | Easy | **Retired** | `gets()` en `run()`, offset `0x38` y ret2win a `winner()` en un binario sin PIE | [Ver](challenges/Reg/README.md) | [EN](challenges/Reg/README.en.md) |
| Survival of the Fittest | Blockchain | Very Easy | **Retired** | `strongAttack(20)` y `loot()` sin control del estado | [Ver](challenges/Survival%20of%20the%20Fittest/README.md) | [EN](challenges/Survival%20of%20the%20Fittest/README.en.md) |
| APKrypt | Mobile | Easy | **Retired** | Clave AES y blob en el APK, cifrado ECB | [Ver](challenges/APKrypt/README.md) | [EN](challenges/APKrypt/README.en.md) |
| Photon Lockdown | Hardware | Very Easy | **Retired** | SquashFS con la contraseña de fábrica en `config_default.xml` | [Ver](challenges/Photon%20Lockdown/README.md) | [EN](challenges/Photon%20Lockdown/README.en.md) |
| Prometheon | AI/ML | Medium | **Retired** | Inyección de prompt en cinco niveles encadenados | [Ver](challenges/Prometheon/README.md) | [EN](challenges/Prometheon/README.en.md) |
| Forks and Knives | Pwn | Medium | **Retired** | Off-by-one, format string, canario por `fork()` y ROP con `dup2` | [Ver](challenges/Forks%20and%20Knives/README.md) | [EN](challenges/Forks%20and%20Knives/README.en.md) |
| Evaluative | Coding | Very Easy | **Retired** | Evaluación polinómica de grado 8 con Horner | [Ver](challenges/Evaluative/README.md) | [EN](challenges/Evaluative/README.en.md) |
| Oddly Even | Coding | Very Easy | **Retired** | Paridad con módulo 2, incluidos cero y negativos | [Ver](challenges/Oddly%20Even/README.md) | [EN](challenges/Oddly%20Even/README.en.md) |
| Threat Index | Coding | Very Easy | **Retired** | Suma ponderada de 18 palabras clave en la cadena | [Ver](challenges/Threat%20Index/README.md) | [EN](challenges/Threat%20Index/README.en.md) |
| Watch Tower | ICS | Very Easy | **Retired** | PCAP Modbus/TCP: la flag está en los `reference numbers` de la función 16 | [Ver](challenges/Watch%20Tower/README.md) | [EN](challenges/Watch%20Tower/README.en.md) |
| Intrusion | ICS | Easy | **Retired** | Planta Modbus: holding registers con `unit id` 52 y lectura automatizada | [Ver](challenges/Intrusion/README.md) | [EN](challenges/Intrusion/README.en.md) |
| Factory | ICS | Easy | **Retired** | Lógica de escalera: modo manual y `Write Single Coil` para vaciar el tanque | [Ver](challenges/Factory/README.md) | [EN](challenges/Factory/README.en.md) |
| Shush Protocol | ICS | Very Easy | **Retired** | Función Modbus 102 propietaria: credenciales en claro en el flujo TCP | [Ver](challenges/Shush%20Protocol/README.md) | [EN](challenges/Shush%20Protocol/README.en.md) |
| Sneak peek | ICS | Easy | **Retired** | Función `0x64`: sobrescribir el MD5 de la contraseña en el bloque de memoria | [Ver](challenges/Sneak%20peek/README.md) | [EN](challenges/Sneak%20peek/README.en.md) |
| FlagCasino | Reversing | Very Easy | **Retired** | `srand` sembrado con cada carácter y comparado contra un array de 30 enteros | [Ver](challenges/FlagCasino/README.md) | [EN](challenges/FlagCasino/README.en.md) |
| Simple Encryptor | Reversing | Very Easy | **Retired** | Semilla de `time()` en los 4 primeros bytes; XOR y `ROL` con `rand()` | [Ver](challenges/Simple%20Encryptor/README.md) | [EN](challenges/Simple%20Encryptor/README.en.md) |
| Shattered Tablet | Reversing | Very Easy | **Retired** | 40 comparaciones `data[i]` mezcladas; reconstruir ordenando por índice | [Ver](challenges/Shattered%20Tablet/README.md) | [EN](challenges/Shattered%20Tablet/README.en.md) |
| Tear or Dear | Reversing | Medium | **Retired** | .NET WinForms: dnSpy de 32 bits y breakpoint en `this.username == this.o` | [Ver](challenges/Tear%20or%20Dear/README.md) | [EN](challenges/Tear%20or%20Dear/README.en.md) |
| Snakecode | Reversing | Easy | **Retired** | `.pyc` de Python 2.7 con `marshal`; la flag aparece en la manzana del juego | [Ver](challenges/Snakecode/README.md) | [EN](challenges/Snakecode/README.en.md) |
| Locked Away | Misc | Easy | **Retired** | PyJail: `blacklist.clear()` y `open_chest()` | [Ver](challenges/Locked%20Away/README.md) | [EN](challenges/Locked%20Away/README.en.md) |
| Hidden Path | Misc | Easy | **Retired** | Carácter invisible `U+3164` como variable y comando inyectado | [Ver](challenges/Hidden%20Path/README.md) | [EN](challenges/Hidden%20Path/README.en.md) |
| Aptitude Test | Misc | Very Easy | **Retired** | Cuestionario por socket: diez respuestas y flag | [Ver](challenges/Aptitude%20Test/README.md) | [EN](challenges/Aptitude%20Test/README.en.md) |
| Chrono Mind | Misc | Easy | **Retired** | Path traversal al contexto del modelo y RCE por autocompletado | [Ver](challenges/Chrono%20Mind/README.md) | [EN](challenges/Chrono%20Mind/README.en.md) |
| Super-Duper Pwn | Misc | Easy | **Retired** | Plantilla de `/checkout` y escape de `vm2` | [Ver](challenges/Super-Duper%20Pwn/README.md) | [EN](challenges/Super-Duper%20Pwn/README.en.md) |

- Logro: https://labs.hackthebox.com/achievement/challenge/4187928/1926
- Índice de categorías y convenciones: [challenges/README.md](challenges/README.md) · [EN](challenges/README.en.md)

---

## 🕵️ Sherlocks

Escenarios de investigación defensiva: no se ataca nada, se responde a preguntas sobre un incidente a partir de evidencias.

| Sherlock | Dominio | Dificultad | Evidencia | ES | EN |
|---|---|---|---|---|---|
| Litter | SOC | Easy | PCAP con túnel DNS (dnscat2) y ZIP del host | [Ver](sherlocks/litter/README.md) | [EN](sherlocks/litter/README.en.md) |
| Jugglin | DFIR / WSL2 | Medium | Capturas de API de `wsl.exe`: exfiltración y `lsassy` sin rastro en logs de Windows | [Ver](sherlocks/jugglin/README.md) | [EN](sherlocks/jugglin/README.en.md) |
| Heist | DFIR / Malware | Hard | `Partnership.pdf.exe` → RedLine, PCAP, Prefetch y SRUM | [Ver](sherlocks/heist/README.md) | [EN](sherlocks/heist/README.en.md) |
| BOughT | DFIR / Malware | Hard | Memoria + AD1, persistencia en `StartUp`, mutex, DGA de 59.049 dominios y DDoS | [Ver](sherlocks/bought/README.md) | [EN](sherlocks/bought/README.en.md) |
| Liberty | DFIR / Windows | Medium | Spray → RDP, robo de Net-NTLMv2 con un `.url` y PowerShell Web Access | [Ver](sherlocks/liberty/README.md) | [EN](sherlocks/liberty/README.en.md) |
| Jinkies | DFIR / Windows | Medium | SMB con credenciales, backup `bk_db.ibd` y reutilización hasta el hash local | [Ver](sherlocks/jinkies/README.md) | [EN](sherlocks/jinkies/README.en.md) |
| i-like-to | DFIR / MOVEit | Easy | CVE-2023-34362: logs de IIS, `$MFT`, EVTX, memoria y volcado SQL | [Ver](sherlocks/i-like-to/README.md) | [EN](sherlocks/i-like-to/README.en.md) |
| Pikaptcha | DFIR / Windows | Easy | Captcha falso, portapapeles y PowerShell: PCAP más triaje KAPE | [Ver](sherlocks/pikaptcha/README.md) | [EN](sherlocks/pikaptcha/README.en.md) |
| Constellation | Threat Intelligence | Medium | PDF con instrucciones a un insider: metadatos y URLs con hora | [Ver](sherlocks/constellation/README.md) | [EN](sherlocks/constellation/README.en.md) |
| Heartbreaker-Continuum | DFIR / Malware | Easy | `.tiff.exe` con PowerShell compilado y exfiltración por SFTP | [Ver](sherlocks/heartbreaker-continuum/README.md) | [EN](sherlocks/heartbreaker-continuum/README.en.md) |
| MisCloud | Cloud / GCP | Medium | Hook de Gitea, cuenta de servicio y bucket: captura más audit logs | [Ver](sherlocks/miscloud/README.md) | [EN](sherlocks/miscloud/README.en.md) |
| Hunter | Threat Hunting | Insane | Servicio 7045, PDF recuperado del índice de Windows, KeePass y CVE-2023-32784 hasta la exfiltración FTP | [Ver](sherlocks/hunter/README.md) | [EN](sherlocks/hunter/README.en.md) |
| Heartbreaker-Denouement | Cloud / AWS | Medium | SSRF a IMDS, credenciales de rol y snapshots de RDS compartidos: CloudTrail en JSONL | [Ver](sherlocks/heartbreaker-denouement/README.md) | [EN](sherlocks/heartbreaker-denouement/README.en.md) |
| Trent | DFIR / Red | Medium | PCAP de un router: CVE-2024-28353 y reverse shell al C2 | [Ver](sherlocks/trent/README.md) | [EN](sherlocks/trent/README.en.md) |

- Índice, metodología y pendientes: [sherlocks/README.md](sherlocks/README.md) · [EN](sherlocks/README.en.md)
- Plantilla de ficha: [templates/sherlock-template.md](templates/sherlock-template.md) · [EN](templates/sherlock-template.en.md)

---

## 🧠 Conocimiento

Notas reutilizables (cada una en español e inglés):

- [Spring Boot Actuator / heapdump](knowledge/web/actuator-heapdump.md) · [EN](knowledge/web/actuator-heapdump.en.md)
- [XXE](knowledge/web/xxe.md) · [EN](knowledge/web/xxe.en.md)
- [XSS al bot admin de WordPress con payload cifrado](knowledge/web/wp-admin-bot-xss.md) · [EN](knowledge/web/wp-admin-bot-xss.en.md)
- [ClickHouse cheatsheet](knowledge/clickhouse/cheatsheet.md) · [EN](knowledge/clickhouse/cheatsheet.en.md)
- [Captura de credenciales en `/proc`](knowledge/linux/proc-credential-capture.md) · [EN](knowledge/linux/proc-credential-capture.en.md)
- [systemd timers y privesc](knowledge/privesc/systemd-timers.md) · [EN](knowledge/privesc/systemd-timers.en.md)
- [Craft CMS: utilidades del panel y secretos del entorno](knowledge/web/craft-cms-cp-utilities.md) · [EN](knowledge/web/craft-cms-cp-utilities.en.md)
- [MSSQL: descifrar credenciales y abusar de SeBackupPrivilege](knowledge/windows/mssql-credentials-sebackup.md) · [EN](knowledge/windows/mssql-credentials-sebackup.en.md)
- [XOR y cadenas de codificaciones](knowledge/crypto/xor-and-encodings.md) · [EN](knowledge/crypto/xor-and-encodings.en.md)
- [RSA: módulo pequeño y RSA de libro](knowledge/crypto/rsa-small-modulus.md) · [EN](knowledge/crypto/rsa-small-modulus.en.md)
- [Cifrados de bloque y cifrados propios](knowledge/crypto/block-ciphers.md) · [EN](knowledge/crypto/block-ciphers.en.md)
- [SSTI: de la plantilla a la ejecución](knowledge/web/ssti.md) · [EN](knowledge/web/ssti.en.md)
- [SQLi en el login: bypass de autenticación](knowledge/web/sqli-auth-bypass.md) · [EN](knowledge/web/sqli-auth-bypass.en.md)
- [Enumeración SMB: sesión nula, shares y credenciales](knowledge/general/smb-enumeration.md) · [EN](knowledge/general/smb-enumeration.en.md)
- [S3 mal configurado: buckets abiertos y webshell](knowledge/cloud/s3-misconfiguration.md) · [EN](knowledge/cloud/s3-misconfiguration.en.md)
- [Log4Shell: de un User-Agent a RCE](knowledge/web/log4shell.md) · [EN](knowledge/web/log4shell.en.md)
- [Deserialización PHP](knowledge/web/php-deserialization.md) · [EN](knowledge/web/php-deserialization.en.md)
- [JWT y contaminación de prototipos](knowledge/web/node-jwt-prototype.md) · [EN](knowledge/web/node-jwt-prototype.en.md)
- [Triaje de PCAP](knowledge/forensics/pcap-triage.md) · [EN](knowledge/forensics/pcap-triage.en.md)
- [Artefactos Windows: EVTX, MFT y Prefetch](knowledge/forensics/windows-artifacts.md) · [EN](knowledge/forensics/windows-artifacts.en.md)
- [Privesc Linux: sudo, SUID, capabilities y cron](knowledge/privesc/linux-sudo-suid.md) · [EN](knowledge/privesc/linux-sudo-suid.en.md)
- [Kerberos: AS-REP, Kerberoast y GPP](knowledge/windows/kerberos-enum.md) · [EN](knowledge/windows/kerberos-enum.en.md)
- [Pivoting: SSH, chisel y Ligolo-ng](knowledge/general/pivoting.md) · [EN](knowledge/general/pivoting.en.md)
- [LFI: de leer ficheros a ejecutar código](knowledge/web/lfi-to-rce.md) · [EN](knowledge/web/lfi-to-rce.en.md)
- [Privesc Windows: SeImpersonate, servicios y LAPS](knowledge/windows/privesc-windows.md) · [EN](knowledge/windows/privesc-windows.en.md)
- [Explotar un CVE: versión, PoC y adaptación](knowledge/web/cve-workflow.md) · [EN](knowledge/web/cve-workflow.en.md)
- [AD CS: ESC13 (política de emisión enlazada a un grupo)](knowledge/windows/adcs-esc13.md) · [EN](knowledge/windows/adcs-esc13.en.md)
- [AD CS: ESC4 → ESC1](knowledge/windows/adcs-esc4-esc1.md) · [EN](knowledge/windows/adcs-esc4-esc1.en.md)
- [gMSA: leer la contraseña gestionada desde el grupo](knowledge/windows/gmsa-read-key.md) · [EN](knowledge/windows/gmsa-read-key.en.md)
- [JEA: endpoints restringidos y PSReadLine](knowledge/windows/jea.md) · [EN](knowledge/windows/jea.en.md)
- [RBCD y S4U2Proxy](knowledge/windows/rbcd-s4u2proxy.md) · [EN](knowledge/windows/rbcd-s4u2proxy.en.md)
- [MSSQL: de sysadmin a SYSTEM y DCSync](knowledge/windows/mssql-exec.md) · [EN](knowledge/windows/mssql-exec.en.md)
- [Reloj y Kerberos: desfase de 5 minutos](knowledge/general/kerberos-clock.md) · [EN](knowledge/general/kerberos-clock.en.md)
- [Cómo entrar: SSH, RDP, WinRM, SMB y claves BitLocker](knowledge/general/remote-access.md) · [EN](knowledge/general/remote-access.en.md)
- [Canal de ataque: VM de Kali, VPN y comprobación previa](knowledge/general/lab-setup.md) · [EN](knowledge/general/lab-setup.en.md)
- [Desbordamiento de pila y ROP en x86-64](knowledge/pwn/rop-stack.md) · [EN](knowledge/pwn/rop-stack.en.md)
- [Infraestructura de phishing: del correo al dominio](knowledge/osint/phishing-infrastructure.md) · [EN](knowledge/osint/phishing-infrastructure.en.md)
- [Esteganografía en imágenes y audio](knowledge/stego/images-audio.md) · [EN](knowledge/stego/images-audio.en.md)
- [Análisis de APK: de `jadx` a Frida](knowledge/mobile/apk-analysis.md) · [EN](knowledge/mobile/apk-analysis.en.md)
- [Hardware: UART, firmware y extracción](knowledge/hardware/uart-firmware.md) · [EN](knowledge/hardware/uart-firmware.en.md)
- [Prototype pollution y AST injection](knowledge/web/prototype-pollution-ast.md) · [EN](knowledge/web/prototype-pollution-ast.en.md)
- [WSL2 en DFIR: artefactos del host y captura de API](knowledge/forensics/wsl2-dfir.md) · [EN](knowledge/forensics/wsl2-dfir.en.md)
- [Cadenas de ACL en AD: de GenericAll a DCSync](knowledge/windows/ad-acl-chains.md) · [EN](knowledge/windows/ad-acl-chains.en.md)
- [RedLine Stealer: cadena de entrega, C2 y artefactos](knowledge/forensics/malware-redline.md) · [EN](knowledge/forensics/malware-redline.en.md)
- [ImageMagick CVE-2022-44268: lectura arbitraria de ficheros](knowledge/linux/imagemagick-file-read.md) · [EN](knowledge/linux/imagemagick-file-read.en.md)
- [AD Recycle Bin: objetos borrados como fuente de credenciales](knowledge/windows/ad-recycle-bin.md) · [EN](knowledge/windows/ad-recycle-bin.en.md)
- [MOVEit CVE-2023-34362: explotación y artefactos para DFIR](knowledge/forensics/moveit-cve-2023-34362.md) · [EN](knowledge/forensics/moveit-cve-2023-34362.en.md)
- [Carrera de `logrotate` con directorio escribible](knowledge/linux/logrotate-race.md) · [EN](knowledge/linux/logrotate-race.en.md)
- [Modbus/TCP en capturas: registros, funciones y extracción](knowledge/ics/modbus-pcap.md) · [EN](knowledge/ics/modbus-pcap.en.md)
- [Entra ID y Sentinel: inicios de sesión, auditoría y KQL](knowledge/cloud/entra-id-sentinel.md) · [EN](knowledge/cloud/entra-id-sentinel.en.md)
- [TeamViewer 7 y CVE-2019-18988: clave AES compartida](knowledge/windows/teamviewer-cve-2019-18988.md) · [EN](knowledge/windows/teamviewer-cve-2019-18988.en.md)
- [Inyección de prompt: sacar lo que el modelo no debe decir](knowledge/ai/prompt-injection.md) · [EN](knowledge/ai/prompt-injection.en.md)
- [Contratos inteligentes: estado, pagos y superficies típicas](knowledge/blockchain/smart-contracts.md) · [EN](knowledge/blockchain/smart-contracts.en.md)
- [PRNG, semillas y esquemas de clave](knowledge/reversing/prng-keyschedule.md) · [EN](knowledge/reversing/prng-keyschedule.en.md)
- [PyJail: listas negras y escapes](knowledge/misc/pyjail-bypass.md) · [EN](knowledge/misc/pyjail-bypass.en.md)
- [Threat hunting: hipótesis, pivotes y evidencia](knowledge/threat-hunting/threat-hunting.md) · [EN](knowledge/threat-hunting/threat-hunting.en.md)
- [Caracteres invisibles y puertas traseras Unicode](knowledge/misc/unicode-invisible.md) · [EN](knowledge/misc/unicode-invisible.en.md)
- [.NET: triaje, dnSpy y depuración](knowledge/reversing/dotnet-dnspy.md) · [EN](knowledge/reversing/dotnet-dnspy.en.md)
- [Inyección de contexto y autocompletado en modelos](knowledge/ai/lm-context-injection.md) · [EN](knowledge/ai/lm-context-injection.en.md)
- [Format strings: leer y escribir con printf](knowledge/pwn/format-strings.md) · [EN](knowledge/pwn/format-strings.en.md)
- [Sobrescritura parcial de direcciones](knowledge/pwn/partial-overwrite.md) · [EN](knowledge/pwn/partial-overwrite.en.md)
- [Cadenas C y bytes nulos: truncado silencioso](knowledge/pwn/null-byte-truncation.md) · [EN](knowledge/pwn/null-byte-truncation.en.md)
- [Canario, PIE y ROP: de la fuga al shell](knowledge/pwn/canary-pie-rop.md) · [EN](knowledge/pwn/canary-pie-rop.en.md)
- [DirtyPipe (CVE-2022-0847): escribir en la page cache](knowledge/linux/kernel-dirty-pipe.md) · [EN](knowledge/linux/kernel-dirty-pipe.en.md)

---

## 🧭 Metodología

1. **Reconocimiento:** `nmap`, vhosts, tecnologías.
2. **Enumeración:** web, SMB, FTP, bases de datos, APIs.
3. **Foothold:** credenciales, vulnerabilidades, XXE, IDOR, etc.
4. **Movimiento lateral:** reutilización de credenciales, pivoting.
5. **Escalada de privilegios:** SUID, capabilities, systemd, backups.
6. **Evidencia y limpieza.**
7. **Mitigación y detección.**

---

## 🛠️ Skills

| Área | Nivel | Evidencia |
|---|---|---|
| Web enumeration | 🟢🟢🟢⚪⚪ | Cap, Stream |
| Linux privesc | 🟢🟢🟢⚪⚪ | Cap, Stream |
| Windows / AD | 🟢⚪⚪⚪⚪ | Dancing |
| Cloud | ⚪⚪⚪⚪⚪ | — |

---

## ✅ Calidad

El hook `.githooks/pre-commit` ejecuta `private/scripts/verify.py` y `private/scripts/audit-indices.py` antes de cada commit. Bloquea el commit si hay enlaces rotos, filas que falten o sobren en los índices, cabeceras de idioma mal o tablas raíz descuadradas.

Para activarlo en un clon nuevo, ejecuta el instalador:

```bash
.githooks/install.sh
```

Comprueba Python 3.8+, que existan el hook y los dos scripts, y solo entonces configura `core.hooksPath`. También puedes hacerlo a mano con `git config core.hooksPath .githooks`.

- Requiere **Python 3.8 o posterior**.
- Los dos scripts viven en `private/scripts/`, que está ignorado por git: cópialos en el clon o el hook bloqueará con `falta ...`.
- Ejecución manual: `.githooks/pre-commit` (o cada script por separado).
- Prueba del hook: `.githooks/test.sh`.
- Desactivarlo: `git config --unset core.hooksPath`.

La configuración es local y no se versiona.

---

## 📁 Estructura

```text
htb-writeups/
├── README.md               # Índice (ES)
├── README.en.md            # Índice (EN)
├── .githooks/
│   ├── pre-commit          # Hook de calidad (enlaces e índices)
│   ├── install.sh          # Comprueba requisitos y activa el hook
│   └── test.sh             # Prueba instalador y bloqueo del hook
├── templates/
│   ├── machine-template.md      # Plantilla de máquinas ES
│   ├── machine-template.en.md   # Plantilla de máquinas EN
│   ├── challenge-template.md    # Plantilla de retos ES
│   ├── challenge-template.en.md # Plantilla de retos EN
│   ├── sherlock-template.md     # Plantilla de Sherlock ES
│   └── sherlock-template.en.md  # Plantilla de Sherlock EN
├── challenges/
│   ├── README.md        # Índice de retos ES/EN
│   ├── README.en.md
│   └── Dark Embargo/    # README.md + README.en.md + exploit.py
├── machines/
│   ├── catalog.md       # Catálogo de máquinas de referencia ES/EN
│   ├── catalog.en.md
│   ├── starting-point/
│   │   ├── README.md    # Índice del itinerario ES/EN
│   │   ├── meow/        # README.md + README.en.md
│   │   └── ...          # 25 fichas: Tier 0, 1 y 2
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
│   └── active/          # máquinas activas: gitignored, no se publican
│       ├── dutybound/
│       ├── stream/
│       ├── layover/
│       ├── connected/
│       └── unclaimed/
├── sherlocks/
│   ├── README.md        # Índice de Sherlocks ES/EN
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
│   └── clickhouse/
└── private/             # ignorado por git: credenciales y flags reales
```

---

## ⚠️ Aviso legal

Todo el contenido se ha realizado en laboratorios autorizados de **Hack The Box**. No se publican flags, credenciales ni claves privadas. El material es exclusivamente educativo.

Los writeups de máquinas **activas** permanecen como borradores privados y solo se publican cuando HTB las marca como **Retired**, respetando la política de la plataforma.

---

## 📄 Licencia

Contenido bajo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Código bajo MIT.
