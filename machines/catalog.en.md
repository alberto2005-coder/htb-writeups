# Retired machine catalogue

**English** | [🇪🇸 Español](catalog.md)

Reference notes for **retired** machines, used to study techniques. Rows marked `ref.` were not played on this profile: they are study material, not an achievement, and carry no flags or credentials. Machines that were played live live in `machines/linux/` or `machines/windows/` and appear in the main index.

## Written

| Machine | OS | Difficulty | Main technique | ES | EN |
|---|---|---|---|---|---|
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
| PingPong | Windows | Insane | Dual AD forest, cross-forest delegation, AD CS ESC1 | [ES](../machines/windows/pingpong/README.md) | [Ver](../machines/windows/pingpong/README.en.md) |
| AirTouch | Linux | Hard | WPA2, PEAP Evil Twin, VPN pivot | [ES](../machines/linux/airtouch/README.md) | [Ver](../machines/linux/airtouch/README.en.md) |
| Eighteen | Windows | Hard | `IMPERSONATE`, Werkzeug, CVE-2025-53779 | [ES](../machines/windows/eighteen/README.md) | [Ver](../machines/windows/eighteen/README.en.md) |
| Sink | Linux | Insane | Smuggling, Gitea, AWS KMS | [ES](../machines/linux/sink/README.md) | [Ver](../machines/linux/sink/README.en.md) |
| Sorcery | Linux | Insane | Cypher, WebAuthn, Kafka, FreeIPA | [ES](../machines/linux/sorcery/README.md) | [Ver](../machines/linux/sorcery/README.en.md) |
| Cobblestone | Linux | Insane | Second-order SQLi, Twig SSTI, Cobbler | [ES](../machines/linux/cobblestone/README.md) | [Ver](../machines/linux/cobblestone/README.en.md) |

## Pending

18 retired machines with material located but no writeup yet. They get written in batches:

**Linux:** Doctor, Frolic, Nibbles, Poison, SolidState, DevArea, Sea.

**Windows:** Devel, Fluffy, Garfield, Interpreter, Kobold, VariaType.

**Not yet classified:** Code, Helix, MonitorsFour, Pirate and Pterodactyl.

## PDF dump

A Spanish-language dump with 164 machine directories, 140 of them holding PDFs (448 PDF and 73 ZIP, ~950 MB). 23 are empty: Ariekei, Bastard, Beep, Brainfuck, Charon, CrimeStoppers, Feline, FluxCapacitor, Fulcrum, Holiday, Inception, Jail, Jeeves, Joker, Lame, Mantis, Minion, Name, Optimum, Shrek, SolidState, Tally, and Smasher (a ZIP only). It is not Markdown: useful as a technique reference, not as text.

## Classification notes

- **PingPong is Insane**, not Hard: the original index files it as Hard, but the weekly drop and several independent sources rate it Insane (Windows, two AD forests).
- **`ref.`** means reference note: the machine was not completed on this profile, so there is no achievement link and no flags are published.
- The cross-inventory of the collections (coverage, duplicates, licences) stays outside the repo in a git-ignored local directory, since it holds third-party material.
