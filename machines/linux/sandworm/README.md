---
machine: Sandworm
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ssti, pgp, firejail, cron, rust, cve-2022-31214]
---

# Sandworm — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un servicio de verificación PGP es vulnerable a SSTI y ejecuta comandos dentro de Firejail. Las credenciales en texto claro permiten SSH; un cron compila un binario Rust con una crate escribible y Firejail CVE-2022-31214 cierra la escalada a root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,443 <IP>
```

Se añade `sandworm.htb` al hosts. La web permite pegar un mensaje firmado y verificar la firma PGP.

## Acceso inicial

El campo de verificación se renderiza con una plantilla. Se prueba SSTI:

```text
{{7*7}}
```

Al confirmarse, se usa una carga para ejecutar comandos. El proceso corre dentro de Firejail, pero permite leer archivos y credenciales del servicio. Con esas credenciales se accede por SSH como `atlas`.

## Movimiento lateral

```bash
pspy64
ls -la /opt
```

Un cron compila y ejecuta un binario Rust. El proyecto usa una crate externa en un directorio escribible; se modifica para que la compilación ejecute una reverse shell como el usuario del cron.

## Escalada a root

Firejail es vulnerable a CVE-2022-31214. Se ejecuta el exploit para crear un sandbox con privilegios y desde ahí `su`:

```bash
./firejail-exploit
```

La shell resultante es root. Se lee la flag y se redacta.

## Evidencia

- Respuesta SSTI y ejecución de comandos.
- Credenciales redactadas y SSH.
- `pspy` y crate modificada.
- Versión de Firejail y exploit.

## Lecciones aprendidas

- SSTI en motores de plantillas lleva a RCE.
- Firejail no sustituye el aislamiento de privilegios.
- Las dependencias externas de un cron son código ejecutable.
- CVE-2022-31214 afecta a versiones antiguas de Firejail.

## Mitigación y detección

- Escapar entradas y no renderizar plantillas con datos de usuario.
- Actualizar Firejail.
- Fijar dependencias y permisos de solo lectura.
- Monitorizar compilaciones y procesos hijos de cron.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2022-31214>
- <https://www.hackthebox.com/machines/sandworm>
- <https://github.com/DominicBreuker/pspy>
