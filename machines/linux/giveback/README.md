---
machine: Giveback
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, wordpress, kubernetes, runc, privesc]
---

# Giveback — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress usa GiveWP, vulnerable a CVE-2024-5932; una cadena POP da shell en el pod de Kubernetes. El pod `legacy-internet-cms` ejecuta PHP 8.1 vulnerable a CVE-2024-4577, lo que permite ser root dentro del contenedor. El token de la service account y la API de Kubernetes llevan a secretos y a SSH como `babywyrm`; en el host, runc CVE-2024-21626 permite escapar y ser root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,30686 <IP>
```

- `22` SSH, `80` WordPress y `30686` una API web.
- La web principal es un sitio de donaciones con WordPress.
- La API expone endpoints internos y un entorno de Kubernetes.

## Enumeración

- `wp-scan` identifica el plugin GiveWP vulnerable a CVE-2024-5932.
- El plugin permite una cadena POP que escribe un archivo PHP.
- Los pods usan una service account con permisos sobre secretos.

## Foothold

Se envía el payload de CVE-2024-5932 y se obtiene ejecución en el pod de WordPress; el webshell permite enumerar el clúster y encontrar el pod `legacy-internet-cms`.

```bash
curl -s 'http://<IP>/wp-admin/admin-ajax.php' --data 'action=give_process_donation&give-form-id=1&...'
```

## Movimiento lateral

El pod legado ejecuta PHP-CGI 8.1, vulnerable a CVE-2024-4577. Se explota para ser root dentro del contenedor y se lee el token de la service account; con él se listan secretos y se obtienen credenciales SSH de `babywyrm`.

```bash
kubectl --token=<TOKEN> --server=https://kubernetes.default.svc get secrets -A
```

## Escalada de privilegios

`babywyrm` puede ejecutar contenedores en el host. Se usa runc CVE-2024-21626 para escapar del contenedor, escribir una clave en `/root/.ssh/authorized_keys` y entrar como root.

```bash
docker run --rm -it -v /:/host <IMAGE> /bin/sh
```

## Evidencia

- GiveWP CVE-2024-5932 y webshell en el pod.
- PHP-CGI CVE-2024-4577 y root en el contenedor.
- Token de service account y secretos de Kubernetes.
- runc CVE-2024-21626 y root en el host.

## Lecciones aprendidas

- Un plugin de WordPress puede ser la puerta a un clúster completo.
- Un pod antiguo con PHP-CGI vulnerable rompe el aislamiento del contenedor.
- Los tokens de service account deben tener el mínimo privilegio.

## Mitigación y detección

- Actualizar GiveWP y PHP; retirar PHP-CGI.
- Aplicar RBAC estricto y rotar tokens de service account.
- Actualizar runc y evitar montar el filesystem del host.

## Referencias

- [0xdf — Giveback](https://0xdf.gitlab.io/2026/02/21/htb-giveback.html)
- [IppSec — Giveback](https://www.youtube.com/watch?v=wNKWDKleH04)
- [Hack The Box — Giveback](https://app.hackthebox.com/machines/giveback)
