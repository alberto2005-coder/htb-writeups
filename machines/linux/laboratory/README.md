---
machine: Laboratory
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, gitlab, cve-2020-10977, suid, path-hijack]
---

# Laboratory — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

GitLab es vulnerable a CVE-2020-10977: lectura arbitraria de archivos que se encadena con la creación de proyectos para ejecutar código. Un repositorio privado entrega credenciales SSH; un SUID `docker-security` llama a `chmod` sin ruta absoluta y permite PATH hijacking.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
curl -s http://laboratory.htb/help | grep -i version
# CVE-2020-10977: lectura de archivos y RCE
python3 gitlab_exploit.py -u http://laboratory.htb -t <TOKEN>
# Tras el acceso
find / -perm -4000 -type f 2>/dev/null
mkdir -p /tmp/bin && printf '#!/bin/sh\n/bin/sh\n' > /tmp/bin/chmod && chmod +x /tmp/bin/chmod
PATH=/tmp/bin:$PATH /usr/local/bin/docker-security
```

## Enumeración

- GitLab con versión anterior a 12.9.0 y registro abierto.
- Repositorio privado con secretos y una clave SSH.
- Binario SUID `docker-security` que ejecuta `chmod` sin ruta absoluta.

## Acceso inicial

Se explota la lectura arbitraria de archivos de GitLab y se encadena con la creación de un proyecto para obtener RCE en el contenedor. Del repositorio privado se recuperan credenciales y una clave que permiten SSH al host.

## Escalada de privilegios

`find / -perm -4000` muestra `docker-security`. El binario llama a `chmod` sin ruta absoluta; se coloca un `chmod` falso al principio de `PATH` y se ejecuta como root.

## Evidencia

- Lectura de archivos de GitLab y ejecución en el contenedor.
- Clave SSH del repositorio privado.
- `docker-security` con `PATH` manipulado y shell de root.

## Lecciones aprendidas

- La lectura arbitraria de archivos puede convertirse en RCE al encadenar funcionalidades.
- Los repositorios privados suelen contener secretos operativos.
- Un SUID que llama a comandos sin ruta absoluta es PATH hijacking.

## Mitigación y detección

- Actualizar GitLab y restringir el registro.
- No guardar claves SSH en repositorios; usar credenciales efímeras.
- Usar rutas absolutas en binarios SUID y revisar capabilities.

## Referencias

- [0xdf — Laboratory](https://0xdf.gitlab.io/2021/04/17/htb-laboratory.html)
- [NVD — CVE-2020-10977](https://nvd.nist.gov/vuln/detail/CVE-2020-10977)
- [Hack The Box — Laboratory](https://app.hackthebox.com/machines/laboratory)
