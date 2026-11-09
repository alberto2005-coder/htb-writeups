# 🎯 HTB Writeups — alberto2005coder

**Español** | [🇬🇧 English](README.en.md)

Repositorio personal de writeups, notas y metodología de **Hack The Box**.

> **Estado:** borradores en construcción. Las máquinas **activas** no se publican hasta que HTB las retire.

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
| Buff | Windows | Easy | Web | **Retired** (ref.) | Subida sin autenticacion, CloudMe 1.11.2 | [Ver](machines/windows/buff/README.md) | [EN](machines/windows/buff/README.en.md) |
| Blackfield | Windows | Hard | Active Directory | **Retired** (ref.) | AS-REP, volcado de lsass, SeBackupPrivilege, NTDS | [Ver](machines/windows/blackfield/README.md) | [EN](machines/windows/blackfield/README.en.md) |
| Explosion | Windows | Very Easy | Starting Point | **Available** | RDP con la cuenta `Administrator` sin contraseña | [Ver](machines/starting-point/explosion/README.md) | [EN](machines/starting-point/explosion/README.en.md) |
| Preignition | Linux | Very Easy | Starting Point | **Available** | Panel `/admin.php` oculto con `admin:admin` | [Ver](machines/starting-point/preignition/README.md) | [EN](machines/starting-point/preignition/README.en.md) |
| Mongod | Linux | Very Easy | Starting Point | **Available** | MongoDB en 27017 sin autenticación | [Ver](machines/starting-point/mongod/README.md) | [EN](machines/starting-point/mongod/README.en.md) |
| Synced | Linux | Very Easy | Starting Point | **Available** | rsync anónimo en 873 | [Ver](machines/starting-point/synced/README.md) | [EN](machines/starting-point/synced/README.en.md) |
| Sequel | Linux | Very Easy | Starting Point | **Available** | MySQL con `root` sin contraseña | [Ver](machines/starting-point/sequel/README.md) | [EN](machines/starting-point/sequel/README.en.md) |
| Cap | Linux | Easy | Machines | **Retired** | IDOR, análisis de pcap, `cap_setuid` | [Ver](machines/linux/cap/README.md) | [EN](machines/linux/cap/README.en.md) |
| MakeSense | Linux | Medium | Season 11 | **Retired** | XSS al bot admin, AES-GCM forjado, plugin malicioso, OCR como root | [Ver](machines/linux/makesense/README.md) | [EN](machines/linux/makesense/README.en.md) |
| DutyBound | Linux | Medium | Season 12 | **Active** | BCBP, SQLi en PostgreSQL, `COPY TO PROGRAM`, X11/XTEST, path unit con `eval` | [Borrador](machines/active/dutybound/README.md) | [EN](machines/active/dutybound/README.en.md) |
| Stream | Linux | Medium | Season 12 | **Active** | Heapdump, XXE, ClickHouse, Kopia, timer root | [Borrador](machines/active/stream/README.md) | [EN](machines/active/stream/README.en.md) |
| Layover | Linux | Medium | Season 12 | **Active** | Credenciales WiFi en texto claro, utilidades del CP de Craft (backup de BD + phpinfo), descifrado Yii, CUPS 2.4.16 CVE-2026-34990 | [Borrador](machines/active/layover/README.md) | [EN](machines/active/layover/README.en.md) |
| Connected | Linux | Easy | Season 11 | **Active** | FreePBX 16: SQLi apilada CVE-2025-57819 + path traversal CVE-2025-61678 hasta webshell, e incron con `init.conf` sourced como root | [Borrador](machines/active/connected/README.md) | [EN](machines/active/connected/README.en.md) |
| Unclaimed | Windows | Medium | Season 12 | **Active** | Chatbot con SQL: `IMPERSONATE` a sysadmin, `xp_cmdshell`, descifrado DPAPI de un credential, y `SeBackupPrivilege` con `robocopy /B` | [Borrador](machines/active/unclaimed/README.md) | [EN](machines/active/unclaimed/README.en.md) |
| Active | Windows | Easy | Machines | **Retired** (ref.) | GPP en SYSVOL, Kerberoasting a `Administrator` | [Ver](machines/windows/active/README.md) | [EN](machines/windows/active/README.en.md) |
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
| PingPong | Windows | Insane | Machines | **Retired** (ref.) | Dos bosques AD, Kerberos AES256, delegación a MSSQL y AD CS ESC1 | [Ver](machines/windows/pingpong/README.md) | [EN](machines/windows/pingpong/README.en.md) |
| AirTouch | Linux | Hard | Machines | **Retired** (ref.) | Handshake WPA2, Evil Twin PEAP-MSCHAPv2 y pivote por VPN | [Ver](machines/linux/airtouch/README.md) | [EN](machines/linux/airtouch/README.en.md) |
| Eighteen | Windows | Hard | Machines | **Retired** (ref.) | `IMPERSONATE` en MSSQL, hash Werkzeug, CVE-2025-53779 (dMSA) | [Ver](machines/windows/eighteen/README.md) | [EN](machines/windows/eighteen/README.en.md) |
| Sink | Linux | Insane | Machines | **Retired** (ref.) | Smuggling CL.TE, Gitea con claves AWS, Secrets Manager y KMS | [Ver](machines/linux/sink/README.md) | [EN](machines/linux/sink/README.en.md) |
| Sorcery | Linux | Insane | Machines | **Retired** (ref.) | Cypher injection, XSS en passkeys, Kafka y FreeIPA | [Ver](machines/linux/sorcery/README.md) | [EN](machines/linux/sorcery/README.en.md) |
| Cobblestone | Linux | Insane | Machines | **Retired** (ref.) | SQLi de segundo orden, XSS, Twig SSTI y CVE-2024-47533 | [Ver](machines/linux/cobblestone/README.md) | [EN](machines/linux/cobblestone/README.en.md) |
| Code | Linux | Easy | Machines | **Retired** (ref.) | Escape de blocklist en Python, bcrypt y `backy.sh` con traversal | [Ver](machines/linux/code/README.md) | [EN](machines/linux/code/README.en.md) |
| Kobold | Linux | Easy | Machines | **Retired** (ref.) | MCPJam Inspector CVE-2026-23744, PrivateBin y contenedor privilegiado | [Ver](machines/linux/kobold/README.md) | [EN](machines/linux/kobold/README.en.md) |
| Helix | Linux | Medium | Machines | **Retired** (ref.) | NiFi 1.21.0, `CREATE ALIAS` de H2 (CVE-2023-34468) y OPC UA | [Ver](machines/linux/helix/README.md) | [EN](machines/linux/helix/README.en.md) |
| Interpreter | Linux | Medium | Machines | **Retired** (ref.) | Mirth Connect CVE-2023-43208, PBKDF2 y `eval()` en servicio local | [Ver](machines/linux/interpreter/README.md) | [EN](machines/linux/interpreter/README.en.md) |
| VariaType | Linux | Medium | Machines | **Retired** (ref.) | fontTools CVE-2025-66034, FontForge CVE-2024-25082 y setuptools CVE-2025-47273 | [Ver](machines/linux/variatype/README.md) | [EN](machines/linux/variatype/README.en.md) |

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

- **Retired:** writeup publicable.
- **Active:** solo borrador privado; se publica cuando HTB retire la máquina.

---

## 🧩 Retos

Retos resueltos. No hay escalada: el objetivo es la flag del reto, así que el writeup se centra en el fallo y en la cadena de explotación.

| Reto | Tipo | Dificultad | Estado | Técnicas clave | ES | EN |
|---|---|---|---|---|---|---|
| Dark Embargo | Web / Pwn | Medium | **Retired** | PHP 8.4.26: OOM en `session.upload_progress` → use-after-free (CVE-2026-109618/109619), leak de ASLR por `Set-Cookie` y `pDestructor` → `system()` | [Ver](challenges/Dark%20Embargo/README.md) | [EN](challenges/Dark%20Embargo/README.en.md) |
| Emdee five for life | Web | Easy | **Retired** | MD5 contra reloj: sesión HTTP, regex y automatización | [Ver](challenges/Emdee%20five%20for%20life/README.md) | [EN](challenges/Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | **Retired** | Inyección LDAP en login y buscador (`*` como comodín) | [Ver](challenges/Phonebook/README.md) | [EN](challenges/Phonebook/README.en.md) |
| Under Construction | Web | Easy | **Retired** | Confusión de algoritmos JWT: firmar HS256 con la clave pública | [Ver](challenges/Under%20Construction/README.md) | [EN](challenges/Under%20Construction/README.en.md) |

- Logro: https://labs.hackthebox.com/achievement/challenge/4187928/1926
- Índice de categorías y convenciones: [challenges/README.md](challenges/README.md) · [EN](challenges/README.en.md)

---

## 🕵️ Sherlocks

Escenarios de investigación defensiva: no se ataca nada, se responde a preguntas sobre un incidente a partir de evidencias.

| Sherlock | Dominio | Dificultad | Evidencia | ES | EN |
|---|---|---|---|---|---|
| Litter | SOC | Easy | PCAP con túnel DNS (dnscat2) y ZIP del host | [Ver](sherlocks/litter/README.md) | [EN](sherlocks/litter/README.en.md) |

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
- [Cómo entrar: SSH, RDP, WinRM, SMB y claves BitLocker](knowledge/general/remote-access.md) · [EN](knowledge/general/remote-access.en.md)
- [Canal de ataque: VM de Kali, VPN y comprobación previa](knowledge/general/lab-setup.md) · [EN](knowledge/general/lab-setup.en.md)

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

## 📁 Estructura

```text
htb-writeups/
├── README.md               # Índice (ES)
├── README.en.md            # Índice (EN)
├── templates/
│   ├── machine-template.md      # Plantilla de máquinas ES
│   ├── machine-template.en.md   # Plantilla de máquinas EN
│   ├── challenge-template.md    # Plantilla de retos ES
│   └── challenge-template.en.md # Plantilla de retos EN
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
│   ├── clickhouse/
│   ├── linux/
│   ├── general/
│   ├── privesc/
│   └── windows/
└── private/             # ignorado por git: credenciales y flags reales
```

---

## ⚠️ Aviso legal

Todo el contenido se ha realizado en laboratorios autorizados de **Hack The Box**. No se publican flags, credenciales ni claves privadas. El material es exclusivamente educativo.

Los writeups de máquinas **activas** permanecen como borradores privados y solo se publican cuando HTB las marca como **Retired**, respetando la política de la plataforma.

---

## 📄 Licencia

Contenido bajo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Código bajo MIT.
