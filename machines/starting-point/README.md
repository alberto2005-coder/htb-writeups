# Starting Point

[🇬🇧 English](README.en.md) | **Español**

Máquinas del itinerario **Starting Point** de Hack The Box. Van en tres tiers lineales (0, 1 y 2) y no son máquinas "normales": cada una entrena un servicio o una técnica concreta. Todas las fichas de esta categoría viven **solo** en este directorio; las máquinas retiradas de dificultad Easy/Medium están en `machines/linux/` y `machines/windows/` según su sistema.

## TL;DR

- Ver las secciones adyacentes para el detalle.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

- Vector de entrada y payload descritos en «Reconocimiento» y «Escalada de privilegios».

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Mitigaciones y detección

- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.
- Deshabilitar el FTP anónimo y sustituirlo por SFTP/FTPS con cuentas nominales.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)

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

## Cómo se resuelven

1. `nmap -sC -sV` y anotar **versión** de cada servicio.
2. Ir al servicio con su propio cliente (`ftp`, `smbclient`, `redis-cli`, `mongosh`, `rsync`, `mysql`, `xfreerdp`).
3. Comprobar credenciales vacías, accesos anónimos y paneles ocultos antes de buscar exploits.
4. La flag suele estar en un fichero del escritorio, en una colección o en una tabla.

## Pendiente

- Confirmar el tier exacto de cada máquina en la plataforma y añadirlo a la tabla.
- Completar las que falten de los tiers 1 y 2 (Appointment, Crocodile, Responder, Three, Ignition, Bike, Pennyworth, Tactics, Archetype, Oopsie, Vaccine…).
