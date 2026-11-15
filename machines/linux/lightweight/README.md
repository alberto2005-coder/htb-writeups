---
machine: Lightweight
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ldap, tcpdump, backup, openssl, capabilities]
---

# Lightweight — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web crea una cuenta SSH al visitarla. Se genera actividad LDAP y se capturan credenciales en texto claro en localhost con `tcpdump`, lo que permite pivotar al primer usuario. Un backup se crackea para el siguiente usuario; root llega con capacidades completas asignadas a una copia de OpenSSL.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,389 <IP>
curl -s http://lightweight.htb/
ssh <USER>@<IP>
# Captura LDAP en loopback
tcpdump -i lo -A -s0 port 389
# Backup
zip2john backup.zip > hash.txt
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
# Capacidades
getcap -r / 2>/dev/null
./openssl_cap setuidgid 0 /bin/sh -c id
```

## Enumeración

- Sitio que registra una cuenta SSH automáticamente.
- LDAP en localhost con autenticación simple.
- Backup protegido y una copia de `openssl` con capabilities.

## Acceso inicial

Se accede con la cuenta creada por la web. Al iniciar sesión se genera tráfico LDAP; `tcpdump` en la interfaz loopback captura el bind en texto claro y revela la contraseña de otro usuario.

## Escalada de privilegios

El backup del segundo usuario se crackea con John. Con esa cuenta se enumeran capacidades y se encuentra una copia de OpenSSL con `cap_setuid`/`cap_setgid`; se usa para lanzar una shell con UID 0.

## Evidencia

- Cuenta SSH creada desde la web.
- Captura LDAP con credenciales en claro.
- Backup crackeado y `openssl` con capacidades ejecutando `id`.

## Lecciones aprendidas

- LDAP simple envía credenciales sin cifrar.
- Los backups locales son diccionarios de contraseñas.
- Una capacidad sobre un binario copiado rompe el mínimo privilegio.

## Mitigación y detección

- Exigir LDAPS o SASL y no usar binds simples.
- Cifrar backups y restringir su lectura.
- Auditar `getcap -r /` y eliminar copias de binarios con capacidades.

## Referencias

- [0xdf — Lightweight](https://0xdf.gitlab.io/2019/05/11/htb-lightweight.html)
- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Hack The Box — Lightweight](https://app.hackthebox.com/machines/lightweight)
