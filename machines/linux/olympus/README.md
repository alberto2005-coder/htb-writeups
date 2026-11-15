---
machine: Olympus
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, xdebug, aircrack-ng, port-knocking, docker, privesc]
---

# Olympus — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Xdebug 2.5.5 expone el puerto 9000 y permite evaluar PHP, lo que da `www-data`. Desde ahí se pivota a un contenedor Olympia, se captura tráfico 802.11 y se crackea la clave `flightoficarus`; esa pista lleva a SSH como `icarus` en 2222. Una transferencia de zona y una nota revelan el port knocking hacia Hades, se entra como `prometheus` y el grupo `docker` permite montar el host y ser root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,53,80,2222 <IP>
nmap -Pn -sU -p53,161 <IP>
```

- `22` filtrado, `2222` SSH, `53` DNS y `80` Apache.
- La web es una imagen de Zeus con `index.php`.
- Las cabeceras incluyen `Xdebug: 2.5.5`.

## Enumeración

- Xdebug acepta la cookie `XDEBUG_SESSION` y conecta al puerto 9000.
- Se implementa un cliente DBGp que evalúa PHP y ejecuta `system()`.
- `nc -e` está disponible en el host, así que se obtiene una reverse shell como `www-data`.
- Desde el contenedor se enumera la red interna y el contenedor `olympia`.

## Foothold

Se accede al contenedor Olympia, donde hay una captura 802.11. `aircrack-ng` recupera la clave `flightoficarus`; la nota sugiere el usuario `icarus` y la contraseña `Too_cl0se_to_th3_Sun`. SSH en `2222` da acceso.

```bash
aircrack-ng -w rockyou.txt capture.cap
ssh icarus@<IP> -p 2222
```

## Movimiento lateral

El contenedor tiene un archivo `help_of_the_gods.txt` y una transferencia de zona DNS revela `ctfolympus.htb` con una nota para `prometheus`: abrir un portal a Hades con los puertos `3456`, `8234` y `62431`, y la contraseña `St34l_th3_F1re!`.

```bash
for p in 3456 8234 62431; do nc -w1 <IP> $p; done
ssh prometheus@<IP>
```

## Escalada de privilegios

`prometheus` pertenece al grupo `docker`. Se lanza un contenedor privilegiado con el sistema de archivos del host montado en `/mnt` y se escribe una clave en `/root/.ssh/authorized_keys`.

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## Evidencia

- Xdebug y RCE por DBGp.
- Contenedor Olympia y captura 802.11.
- `icarus` por SSH y nota de Hades.
- Port knocking y `prometheus`.
- Grupo `docker` y root.

## Lecciones aprendidas

- Xdebug expuesto es ejecución remota de PHP.
- Las capturas inalámbricas pueden contener contraseñas reutilizables.
- El port knocking no es autenticación, solo ocultación.
- Pertenecer a `docker` equivale a root en el host.

## Mitigación y detección

- Deshabilitar Xdebug en producción y bloquear el puerto 9000.
- No reutilizar claves de WiFi como contraseñas de sistema.
- No confiar en port knocking; exigir autenticación real.
- Restringir el grupo `docker` y usar rootless containers.

## Referencias

- [0xdf — Olympus](https://0xdf.gitlab.io/2018/09/22/htb-olympus.html)
- [IppSec — Olympus](https://www.youtube.com/watch?v=7ifJOon5-G8)
- [Hack The Box — Olympus](https://app.hackthebox.com/machines/olympus)
