# Starting Point

[⚑ English](README.en.md) | **Español**

Itinerario de iniciación de Hack The Box: máquinas cortas, en tiers lineales, donde cada una entrena **un servicio** y su mala configuración típica. No son cajas de dificultad Easy/Medium retiradas —esas viven en `machines/linux/` y `machines/windows/`— sino ejercicios guiados: el objetivo es interiorizar la enumeración antes de encadenar vulnerabilidades.

## Cómo se trabajan

1. Desplegar la instancia en la plataforma y conectarse a la VPN.
2. `nmap -Pn -sV -p-` sobre la IP: la superficie es mínima a propósito.
3. Enumerar el servicio con su cliente nativo (`telnet`, `ftp`, `smbclient`, `redis-cli`, `mongo`, un navegador…).
4. Explotar la configuración por defecto y leer la flag del servicio o del sistema de ficheros.

## Fichas

| Máquina | OS | Servicio | Concepto | ES | EN |
|---|---|---|---|---|---|
| Meow | Linux | 23/telnet | `root` sin contraseña | [Ver](meow/README.md) | [EN](meow/README.en.md) |
| Fawn | Linux | 21/ftp | Acceso anónimo y `get flag.txt` | [Ver](fawn/README.md) | [EN](fawn/README.en.md) |
| Dancing | Windows | 445/smb | Sesión nula y share `WorkShares` | [Ver](dancing/README.md) | [EN](dancing/README.en.md) |
| Redeemer | Linux | 6379/redis | Redis sin `AUTH` y `keys *` | [Ver](redeemer/README.md) | [EN](redeemer/README.en.md) |
| Explosion | Windows | 3389/rdp | `Administrator` con contraseña vacía | [Ver](explosion/README.md) | [EN](explosion/README.en.md) |
| Preignition | Linux | 80/http | `/admin.php` oculto y `admin:admin` | [Ver](preignition/README.md) | [EN](preignition/README.en.md) |
| Mongod | Linux | 27017/mongo | MongoDB sin `--auth` | [Ver](mongod/README.md) | [EN](mongod/README.en.md) |

## Lecciones transversales

- El servicio que responde «sin credenciales» **es** el hallazgo: sesión nula en SMB, FTP anónimo, Redis abierto, MongoDB sin `--auth`, Telnet con `root` vacío.
- Cada protocolo tiene su cliente: `smbclient -L //IP -N`, `ftp` con `anonymous`, `redis-cli`, `mongosh`, `xfreerdp /cert:ignore`.
- La flag casi nunca requiere escalada: está en el recurso compartido, en la base de datos o en el escritorio del administrador.
- Lo aprendido se traslada: los mismos servicios aparecen en cajas Easy/Medium, pero allí con un paso más de enumeración.

## Mitigaciones de referencia

- SMB: firmar y cifrar, deshabilitar SMBv1, retirar la sesión nula y limitar shares administrativos por grupo.
- FTP: prohibir `anonymous` y usar SFTP/FTPS con cuentas nominales.
- Telnet: retirarlo; SSH con contraseña fuerte y `PermitRootLogin no`.
- Redis y MongoDB: `requirepass`/`--auth`, bind a loopback y ACLs por base.
- RDP: contraseñas no vacías, NLA obligatorio y MFA.
- Detección: 4624 tipo 3 con NTLM anónimo, `230 Login successful` de `anonymous`, `INFO`/`keys *` sin `AUTH` y `show dbs` sin autenticación.
