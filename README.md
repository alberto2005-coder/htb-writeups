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
| Meow | Linux | Very Easy | Starting Point | **Retired** | FTP/Telnet sin credenciales | [Ver](machines/starting-point/meow/README.md) | [EN](machines/starting-point/meow/README.en.md) |
| Fawn | Linux | Very Easy | Starting Point | **Retired** | FTP anónimo | [Ver](machines/starting-point/fawn/README.md) | [EN](machines/starting-point/fawn/README.en.md) |
| Dancing | Windows | Very Easy | Starting Point | **Retired** | SMB null session | [Ver](machines/starting-point/dancing/README.md) | [EN](machines/starting-point/dancing/README.en.md) |
| Redeemer | Linux | Very Easy | Starting Point | **Retired** | Redis sin autenticación | [Ver](machines/starting-point/redeemer/README.md) | [EN](machines/starting-point/redeemer/README.en.md) |
| Cap | Linux | Easy | Machines | **Retired** | IDOR, análisis de pcap, `cap_setuid` | [Ver](machines/linux/cap/README.md) | [EN](machines/linux/cap/README.en.md) |
| MakeSense | Linux | Medium | Season 11 | **Retired** | XSS al bot admin, AES-GCM forjado, plugin malicioso, OCR como root | [Ver](machines/linux/makesense/README.md) | [EN](machines/linux/makesense/README.en.md) |
| DutyBound | Linux | Medium | Season 12 | **Active** | BCBP, SQLi en PostgreSQL, `COPY TO PROGRAM`, X11/XTEST, path unit con `eval` | [Borrador](machines/active/dutybound/README.md) | [EN](machines/active/dutybound/README.en.md) |
| Stream | Linux | Medium | Season 12 | **Active** | Heapdump, XXE, ClickHouse, Kopia, timer root | [Borrador](machines/active/stream/README.md) | [EN](machines/active/stream/README.en.md) |

### 🏅 Logros verificables

Cada fila de la tabla anterior corresponde a una máquina completada en el perfil. Los enlaces son la prueba pública del logro:

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

### Leyenda de estados

- **Retired:** writeup publicable.
- **Active:** solo borrador privado; se publica cuando HTB retire la máquina.

---

## 🧠 Conocimiento

Notas reutilizables (cada una en español e inglés):

- [Spring Boot Actuator / heapdump](knowledge/web/actuator-heapdump.md) · [EN](knowledge/web/actuator-heapdump.en.md)
- [XXE](knowledge/web/xxe.md) · [EN](knowledge/web/xxe.en.md)
- [XSS al bot admin de WordPress con payload cifrado](knowledge/web/wp-admin-bot-xss.md) · [EN](knowledge/web/wp-admin-bot-xss.en.md)
- [ClickHouse cheatsheet](knowledge/clickhouse/cheatsheet.md) · [EN](knowledge/clickhouse/cheatsheet.en.md)
- [Captura de credenciales en `/proc`](knowledge/linux/proc-credential-capture.md) · [EN](knowledge/linux/proc-credential-capture.en.md)
- [systemd timers y privesc](knowledge/privesc/systemd-timers.md) · [EN](knowledge/privesc/systemd-timers.en.md)
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
│   ├── machine-template.md      # Plantilla ES
│   └── machine-template.en.md   # Plantilla EN
├── machines/
│   ├── starting-point/
│   │   ├── meow/        # README.md + README.en.md
│   │   ├── fawn/
│   │   ├── dancing/
│   │   └── redeemer/
│   ├── linux/
│   │   ├── cap/
│   │   └── makesense/
│   └── active/          # máquinas activas: gitignored, no se publican
│       ├── dutybound/
│       └── stream/
├── knowledge/
│   ├── web/
│   ├── clickhouse/
│   ├── linux/
│   ├── general/
│   └── privesc/
└── private/             # ignorado por git: credenciales y flags reales
```

---

## ⚠️ Aviso legal

Todo el contenido se ha realizado en laboratorios autorizados de **Hack The Box**. No se publican flags, credenciales ni claves privadas. El material es exclusivamente educativo.

Los writeups de máquinas **activas** permanecen como borradores privados y solo se publican cuando HTB las marca como **Retired**, respetando la política de la plataforma.

---

## 📄 Licencia

Contenido bajo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Código bajo MIT.
