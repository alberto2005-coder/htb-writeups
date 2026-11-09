# Starting Point

[🇬🇧 English](README.en.md) | **Español**

Máquinas del itinerario **Starting Point** de Hack The Box. Van en tres tiers lineales (0, 1 y 2) y no son máquinas "normales": cada una entrena un servicio o una técnica concreta. Todas las fichas de esta categoría viven **solo** en este directorio; las máquinas retiradas de dificultad Easy/Medium están en `machines/linux/` y `machines/windows/` según su sistema.

## Fichas

| Máquina | OS | Concepto | Estado | ES | EN |
|---|---|---|---|---|---|
| Meow | Linux | FTP y Telnet sin credenciales | 100% | [Ver](meow/README.md) | [EN](meow/README.en.md) |
| Fawn | Linux | FTP anónimo | 100% | [Ver](fawn/README.md) | [EN](fawn/README.en.md) |
| Dancing | Windows | SMB sin sesión | 100% | [Ver](dancing/README.md) | [EN](dancing/README.en.md) |
| Redeemer | Linux | Redis sin autenticación | 100% | [Ver](redeemer/README.md) | [EN](redeemer/README.en.md) |
| Explosion | Windows | RDP con contraseña vacía | pendiente | [Ver](explosion/README.md) | [EN](explosion/README.en.md) |
| Preignition | Linux | Panel oculto y credenciales por defecto | pendiente | [Ver](preignition/README.md) | [EN](preignition/README.en.md) |
| Mongod | Linux | MongoDB sin `--auth` | pendiente | [Ver](mongod/README.md) | [EN](mongod/README.en.md) |
| Synced | Linux | rsync anónimo | pendiente | [Ver](synced/README.md) | [EN](synced/README.en.md) |
| Sequel | Linux | MySQL con `root` sin contraseña | pendiente | [Ver](sequel/README.md) | [EN](sequel/README.en.md) |

> "100%" y "pendiente" reflejan lo que aparece en el perfil de HTB, no si la ficha está escrita. Todas las fichas de la tabla están escritas.

## Cómo se resuelven

1. `nmap -sC -sV` y anotar **versión** de cada servicio.
2. Ir al servicio con su propio cliente (`ftp`, `smbclient`, `redis-cli`, `mongosh`, `rsync`, `mysql`, `xfreerdp`).
3. Comprobar credenciales vacías, accesos anónimos y paneles ocultos antes de buscar exploits.
4. La flag suele estar en un fichero del escritorio, en una colección o en una tabla.

## Pendiente

- Confirmar el tier exacto de cada máquina en la plataforma y añadirlo a la tabla.
- Completar las que falten de los tiers 1 y 2 (Appointment, Crocodile, Responder, Three, Ignition, Bike, Pennyworth, Tactics, Archetype, Oopsie, Vaccine…).
