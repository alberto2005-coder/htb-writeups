---
machine: Static
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, totp, vpn, xdebug, php-fpm, format-string, easy-rsa]
---

# Static — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un backup SQL gzip corrupto permite recuperar la semilla TOTP y entrar en el panel interno, que entrega una configuración VPN. En la red interna, un host web con xdebug permite RCE y desde ahí se pivota al host PKI, donde PHP-FPM es vulnerable a CVE-2019-11043. La escalada final abusa de `ersatool`, con `cap_setuid` y una cadena de formato que sobrescribe `ERSA_DIR` para ejecutar un `easyrsa` controlado como root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,2222,8080 <IP>
gobuster dir -u http://<IP>:8080 -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt
```

## Enumeración

- Dos SSH de versiones distintas sugieren contenedores Docker.
- El backup SQL está truncado, pero conserva la semilla del TOTP.
- El panel interno muestra hosts `172.20.0.10` (web) y `172.20.0.11` (pki).

## Acceso inicial

Se repara el gzip y se extrae la semilla TOTP para generar el código y entrar en el panel, que permite descargar una configuración VPN. Con la VPN se llega a `172.20.0.10`, cuyo xdebug expone ejecución remota y da `www-data`. Desde ahí se pivota a `172.20.0.11`, donde CVE-2019-11043 en PHP-FPM permite una shell como `www-data`.

## Escalada de privilegios

`ersatool` tiene `cap_setuid` y una cadena de formato en `printCN`. Se filtra la dirección de `EXT`, se calcula `ERSA_DIR`, se sobrescribe con una ruta escribible y se coloca un script `easyrsa` que copia bash y le pone SUID. Al ejecutar `create`, el binario llama a `system` después de `setuid(0)` y se obtiene root.

## Evidencia

- TOTP válido y configuración VPN descargada.
- Shell en `web` y `pki` mediante xdebug y PHP-FPM.
- `ERSA_DIR` sobrescrito y bash SUID ejecutada.

## Lecciones aprendidas

- Los backups corruptos pueden conservar secretos suficientes.
- xdebug nunca debe estar expuesto en producción.
- Una capacidad `cap_setuid` convierte un binario en root potencial.

## Mitigación y detección

- Cifrar backups y proteger las semillas TOTP.
- Deshabilitar xdebug y actualizar PHP-FPM/Nginx.
- Eliminar capacidades innecesarias y revisar format strings en C.

## Referencias

- [0xdf — Static](https://0xdf.gitlab.io/2021/12/18/htb-static.html)
- [IppSec — Static](https://www.youtube.com/watch?v=XZd-pQTu4vU)
- [Hack The Box — Static](https://app.hackthebox.com/machines/static)
