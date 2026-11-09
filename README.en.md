# 🎯 HTB Writeups — alberto2005coder

[🇪🇸 Español](README.md) | **English**

Personal repository of **Hack The Box** writeups, notes and methodology.

> **Status:** work in progress. **Active** machines are not published until HTB retires them.

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
| Cap | Linux | Easy | Machines | Retired | IDOR, pcap analysis, `cap_setuid` | [ES](machines/linux/cap/README.md) | [Ver](machines/linux/cap/README.en.md) |
| MakeSense | Linux | Medium | Season 11 | Retired | Admin-bot XSS, forged AES-GCM, malicious plugin, OCR as root | [ES](machines/linux/makesense/README.md) | [Ver](machines/linux/makesense/README.en.md) |
| DutyBound | Linux | Medium | Season 12 | **Active** | BCBP, PostgreSQL SQLi, `COPY TO PROGRAM`, X11/XTEST, path unit with `eval` | [ES](machines/active/dutybound/README.md) | [Draft](machines/active/dutybound/README.en.md) |
| Stream | Linux | Medium | Season 12 | **Active** | Heapdump, XXE, ClickHouse, Kopia, root timer | [ES](machines/active/stream/README.md) | [Draft](machines/active/stream/README.en.md) |
| Layover | Linux | Medium | Season 12 | **Active** | Cleartext WiFi credentials, Craft CP utilities (DB backup + phpinfo), Yii decryption, CUPS 2.4.16 CVE-2026-34990 | [ES](machines/active/layover/README.md) | [Draft](machines/active/layover/README.en.md) |
| Connected | Linux | Easy | Season 11 | **Active** | FreePBX 16: stacked SQLi CVE-2025-57819 + path traversal CVE-2025-61678 to webshell, then incron with a root-sourced `init.conf` | [ES](machines/active/connected/README.md) | [Draft](machines/active/connected/README.en.md) |
| Unclaimed | Windows | Medium | Season 12 | **Active** | Chatbot over SQL: `IMPERSONATE` to sysadmin, `xp_cmdshell`, DPAPI decryption of a credential, and `SeBackupPrivilege` with `robocopy /B` | [ES](machines/active/unclaimed/README.md) | [Draft](machines/active/unclaimed/README.en.md) |
| Active | Windows | Easy | Machines | **Retired** (ref.) | GPP in SYSVOL, Kerberoasting `Administrator` | [ES](machines/windows/active/README.md) | [Ver](machines/windows/active/README.en.md) |
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
| PingPong | Windows | Insane | Machines | **Retired** (ref.) | Dual AD forest, AES256 Kerberos, MSSQL delegation and AD CS ESC1 | [ES](machines/windows/pingpong/README.md) | [Ver](machines/windows/pingpong/README.en.md) |
| AirTouch | Linux | Hard | Machines | **Retired** (ref.) | WPA2 handshake, PEAP-MSCHAPv2 Evil Twin and VPN pivot | [ES](machines/linux/airtouch/README.md) | [Ver](machines/linux/airtouch/README.en.md) |
| Eighteen | Windows | Hard | Machines | **Retired** (ref.) | MSSQL `IMPERSONATE`, Werkzeug hash, CVE-2025-53779 (dMSA) | [ES](machines/windows/eighteen/README.md) | [Ver](machines/windows/eighteen/README.en.md) |
| Sink | Linux | Insane | Machines | **Retired** (ref.) | CL.TE smuggling, Gitea with AWS keys, Secrets Manager and KMS | [ES](machines/linux/sink/README.md) | [Ver](machines/linux/sink/README.en.md) |
| Sorcery | Linux | Insane | Machines | **Retired** (ref.) | Cypher injection, passkey XSS, Kafka and FreeIPA | [ES](machines/linux/sorcery/README.md) | [Ver](machines/linux/sorcery/README.en.md) |
| Cobblestone | Linux | Insane | Machines | **Retired** (ref.) | Second-order SQLi, XSS, Twig SSTI and CVE-2024-47533 | [ES](machines/linux/cobblestone/README.md) | [Ver](machines/linux/cobblestone/README.en.md) |

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

- **Retired:** publishable writeup.
- **Active:** private draft only; published once HTB retires the machine.

---

## 🧩 Challenges

Solved challenges. There is no privilege escalation: the goal is the challenge flag, so the writeup focuses on the bug and the exploitation chain.

| Challenge | Type | Difficulty | State | Key techniques | ES | EN |
|---|---|---|---|---|---|---|
| Dark Embargo | Web / Pwn | Medium | **Retired** | PHP 8.4.26: OOM in `session.upload_progress` → use-after-free (CVE-2026-109618/619), ASLR leak via `Set-Cookie`, `pDestructor` → `system()` | [ES](challenges/Dark%20Embargo/README.md) | [Ver](challenges/Dark%20Embargo/README.en.md) |
| Emdee five for life | Web | Easy | **Retired** | MD5 against the clock: session handling, regex, automation | [ES](challenges/Emdee%20five%20for%20life/README.md) | [Ver](challenges/Emdee%20five%20for%20life/README.en.md) |
| Phonebook | Web | Easy | **Retired** | LDAP injection in login and search (`*` wildcard) | [ES](challenges/Phonebook/README.md) | [Ver](challenges/Phonebook/README.en.md) |
| Under Construction | Web | Easy | **Retired** | JWT algorithm confusion: sign HS256 with the public key | [ES](challenges/Under%20Construction/README.md) | [Ver](challenges/Under%20Construction/README.en.md) |

- Achievement: https://labs.hackthebox.com/achievement/challenge/4187928/1926
- Category index and conventions: [challenges/README.en.md](challenges/README.en.md) · [ES](challenges/README.md)

---

## 🕵️ Sherlocks

Defensive investigation scenarios: nothing is attacked, you answer questions about an incident from evidence.

| Sherlock | Domain | Difficulty | Evidence | ES | EN |
|---|---|---|---|---|---|
| Litter | SOC | Easy | PCAP with DNS tunnelling (dnscat2) and host ZIP | [ES](sherlocks/litter/README.md) | [Ver](sherlocks/litter/README.en.md) |

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
- [Getting in: SSH, RDP, WinRM, SMB and BitLocker keys](knowledge/general/remote-access.en.md) · [ES](knowledge/general/remote-access.md)
- [Attack channel: Kali VM, VPN and preflight check](knowledge/general/lab-setup.en.md) · [ES](knowledge/general/lab-setup.md)

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
│   │   ├── meow/        # README.md + README.en.md
│   │   ├── fawn/
│   │   ├── dancing/
│   │   └── redeemer/
│   ├── linux/
│   │   ├── cap/
│   │   ├── makesense/
│   │   ├── admirer/
│   │   ├── airtouch/
│   │   ├── armageddon/
│   │   ├── bank/
│   │   ├── cobblestone/
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
