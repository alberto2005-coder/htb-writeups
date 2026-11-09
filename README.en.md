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

> **States:** **Available** = Starting Point, always available and publishable · **Retired** = retired, publishable · **Active** = in its season, not published until HTB retires it.

### 🏅 Verifiable achievements

Every row in the table above maps to a machine completed on the profile. These links are the public proof:

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

- Achievement: https://labs.hackthebox.com/achievement/challenge/4187928/1926

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
│   └── Dark Embargo/    # README.md + README.en.md + exploit.py
├── machines/
│   ├── starting-point/
│   │   ├── meow/        # README.md + README.en.md
│   │   ├── fawn/
│   │   ├── dancing/
│   │   └── redeemer/
│   ├── linux/
│   │   ├── cap/
│   │   └── makesense/
│   └── active/          # active machines: gitignored, not published
│       ├── dutybound/
│       ├── stream/
│       ├── layover/
│       ├── connected/
│       └── unclaimed/
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
