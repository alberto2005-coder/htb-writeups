# Starting Point

[⚑ English](README.en.md) | **Español**

Itinerario de iniciación de Hack The Box: máquinas cortas, en tiers lineales, donde cada una entrena **un servicio** y su mala configuración típica. No son cajas de dificultad Easy/Medium retiradas —esas viven en `machines/linux/` y `machines/windows/`— sino ejercicios guiados: el objetivo es interiorizar la enumeración antes de encadenar vulnerabilidades.

## Cómo se trabajan

1. Desplegar la instancia en la plataforma y conectarse a la VPN.
2. `nmap -Pn -sV -p-` sobre la IP: la superficie es mínima a propósito.
3. Enumerar el servicio con su cliente nativo (`telnet`, `ftp`, `smbclient`, `redis-cli`, `mongo`, un navegador…).
4. Explotar la configuración por defecto y leer la flag del servicio o del sistema de ficheros.

## Fichas

| Máquina | Tier | OS | Servicio | Concepto | ES | EN |
|---|---|---|---|---|---|---|
| Meow | 0 | Linux | 23/telnet | `root` sin contraseña | [Ver](meow/README.md) | [EN](meow/README.en.md) |
| Fawn | 0 | Linux | 21/ftp | Acceso anónimo y `get flag.txt` | [Ver](fawn/README.md) | [EN](fawn/README.en.md) |
| Dancing | 0 | Windows | 445/smb | Sesión nula y share `WorkShares` | [Ver](dancing/README.md) | [EN](dancing/README.en.md) |
| Redeemer | 0 | Linux | 6379/redis | Redis sin `AUTH` y `keys *` | [Ver](redeemer/README.md) | [EN](redeemer/README.en.md) |
| Explosion | 0 | Windows | 3389/rdp | `Administrator` con contraseña vacía | [Ver](explosion/README.md) | [EN](explosion/README.en.md) |
| Preignition | 0 | Linux | 80/http | `/admin.php` oculto y `admin:admin` | [Ver](preignition/README.md) | [EN](preignition/README.en.md) |
| Mongod | 0 | Linux | 27017/mongo | MongoDB sin `--auth` | [Ver](mongod/README.md) | [EN](mongod/README.en.md) |
| Synced | 0 | Linux | 873/rsync | Módulo anónimo y `rsync` sin credenciales | [Ver](synced/README.md) | [EN](synced/README.en.md) |
| Appointment | 1 | Linux | 80/http | SQLi en el login con `' or '1'='1'#` | [Ver](appointment/README.md) | [EN](appointment/README.en.md) |
| Sequel | 1 | Linux | 3306/mysql | `root` sin contraseña y `show databases` | [Ver](sequel/README.md) | [EN](sequel/README.en.md) |
| Crocodile | 1 | Linux | 21/ftp + 80/http | FTP anónimo con usuarios y contraseñas | [Ver](crocodile/README.md) | [EN](crocodile/README.en.md) |
| Responder | 1 | Windows | 80/http + 5985/winrm | LFI a UNC, hash NetNTLMv2 y WinRM | [Ver](responder/README.md) | [EN](responder/README.en.md) |
| Three | 1 | Linux | 80/http + S3 | Bucket sin autenticación y webshell | [Ver](three/README.md) | [EN](three/README.en.md) |
| Ignition | 1 | Linux | 80/http | Magento con `admin:qwerty123` | [Ver](ignition/README.md) | [EN](ignition/README.en.md) |
| Bike | 1 | Linux | 80/http | SSTI de Handlebars hasta root | [Ver](bike/README.md) | [EN](bike/README.en.md) |
| Funnel | 1 | Linux | 21/ftp + 22/ssh | Spray SSH y túnel al PostgreSQL interno | [Ver](funnel/README.md) | [EN](funnel/README.en.md) |
| Pennyworth | 1 | Linux | 8080/http | Jenkins `root:password` y consola Groovy | [Ver](pennyworth/README.md) | [EN](pennyworth/README.en.md) |
| Tactics | 1 | Windows | 445/smb | Sesión nula y `Administrator` vacío | [Ver](tactics/README.md) | [EN](tactics/README.en.md) |
| Archetype | 2 | Windows | 445/smb + 1433/mssql | Config de SSIS, `xp_cmdshell` y psexec | [Ver](archetype/README.md) | [EN](archetype/README.en.md) |
| Oopsie | 2 | Linux | 80/http | IDOR en cookies, subida y SUID con `PATH` | [Ver](oopsie/README.md) | [EN](oopsie/README.en.md) |
| Vaccine | 2 | Linux | 21/ftp + 80/http | Backup, SQLi con `--os-shell` y `sudo vi` | [Ver](vaccine/README.md) | [EN](vaccine/README.en.md) |
| Unified | 2 | Linux | 8443/https | Log4Shell en UniFi y MongoDB 27117 | [Ver](unified/README.md) | [EN](unified/README.en.md) |
| Included | 2 | Linux | 80/http + 69/udp | LFI, TFTP sin auth y grupo `lxd` | [Ver](included/README.md) | [EN](included/README.en.md) |
| Markup | 2 | Windows | 80/http + 22/ssh | XXE a `id_rsa` y `job.bat` programado | [Ver](markup/README.md) | [EN](markup/README.en.md) |
| Base | 2 | Linux | 80/http | `strcmp` con arrays, subida y `sudo find` | [Ver](base/README.md) | [EN](base/README.en.md) |

> **Tiers:** el Tier 0 son las ocho primeras (Meow → Synced) y está completo. Tier 1 son Appointment → Tactics (nueve) y Tier 2 Archetype → Base (siete). Total: **25 fichas**, todas en ES/EN.

## Lecciones transversales

- El servicio que responde «sin credenciales» **es** el hallazgo: sesión nula en SMB, FTP anónimo, Redis abierto, MongoDB sin `--auth`, Telnet con `root` vacío, un bucket S3 sin IAM.
- Cada protocolo tiene su cliente: `smbclient -L //IP -N`, `ftp` con `anonymous`, `redis-cli`, `mongosh`, `xfreerdp /cert:ignore`, `aws --endpoint`.
- La flag casi nunca requiere escalada: está en el recurso compartido, en la base de datos o en el escritorio del administrador. En Tier 2 sí aparece el paso de usuario a root.
- Lo aprendido se traslada: los mismos servicios aparecen en cajas Easy/Medium, pero allí con un paso más de enumeración.

## Mitigaciones de referencia

- SMB: firmar y cifrar, deshabilitar SMBv1, retirar la sesión nula y limitar shares administrativos por grupo.
- FTP: prohibir `anonymous` y usar SFTP/FTPS con cuentas nominales.
- Telnet: retirarlo; SSH con contraseña fuerte y `PermitRootLogin no`.
- Redis y MongoDB: `requirepass`/`--auth`, bind a loopback y ACLs por base.
- RDP: contraseñas no vacías, NLA obligatorio y MFA.
- Web: consultas preparadas, sin `eval` ni plantillas con entrada del usuario, subidas fuera del webroot.
- Detección: 4624 tipo 3 con NTLM anónimo, `230 Login successful` de `anonymous`, `INFO`/`keys *` sin `AUTH`, `show dbs` sin autenticación y `PUT` a buckets desde IPs no habituales.
