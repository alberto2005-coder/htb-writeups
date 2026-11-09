# Catálogo de máquinas retiradas

[🇬🇧 English](catalog.en.md) | **Español**

Fichas de máquinas **retiradas** que sirven para estudiar técnicas. Las marcadas como `ref.` no se han jugado en este perfil: son material de estudio, no un logro, y no llevan flags ni credenciales. Las que sí están jugadas viven en `machines/linux/` o `machines/windows/` y aparecen en el índice principal.

## Escritas

| Máquina | OS | Dificultad | Técnica principal | ES | EN |
|---|---|---|---|---|---|
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

## Pendientes

24 máquinas retiradas con material localizado y todavía sin ficha propia. Se escriben en lotes:

**Linux:** Doctor, Frolic, Nibbles, Poison, SolidState, DevArea, Sea.

**Windows:** Devel, Fluffy, Garfield, Interpreter, Kobold, VariaType, Eighteen, Active Directory de varios bosques.

**Sin clasificar todavía:** AirTouch, Cobblestone, Code, Helix, MonitorsFour, Pirate, Pterodactyl, Sink, Sorcery y **PingPong** (ver nota de clasificación).

## Volcado en PDF

Un volcado en español de 164 directorios de máquina, 140 con PDF (448 PDF y 73 ZIP, ~950 MB). 23 están vacíos: Ariekei, Bastard, Beep, Brainfuck, Charon, CrimeStoppers, Feline, FluxCapacitor, Fulcrum, Holiday, Inception, Jail, Jeeves, Joker, Lame, Mantis, Minion, Name, Optimum, Shrek, SolidState, Tally, y Smasher (solo un ZIP). No es Markdown: sirve como referencia de técnicas, no como texto.

## Notas de clasificación

- **PingPong es Insane**, no Hard: el índice de origen lo lista como Hard, pero el lanzamiento semanal y varias fuentes independientes lo dan como Insane (Windows, dos bosques de AD).
- **`ref.`** significa ficha de referencia: la máquina no se ha completado en este perfil, así que no hay enlace de logro ni se publican flags.
- El inventario cruzado de las colecciones (cobertura, duplicados, licencias) queda fuera del repo, en un directorio local ignorado por git, porque incluye material de terceros.
