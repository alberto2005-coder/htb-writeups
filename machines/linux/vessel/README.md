---
machine: Vessel
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nodejs, mysql, owa, crio, privesc]
---

# Vessel — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`/.git` en `/dev` permite reconstruir el código con `git-dumper`. El login de mysqljs es vulnerable a type confusion (`password.password=1`) y da acceso al panel, donde OWA 1.7.3 tiene CVE-2022-24637. Un binario PyInstaller y un PDF protegido filtran credenciales de SSH; el SUID `pinns` permite escapar con CVE-2022-0811.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 22.04 y `80/tcp` nginx con `vessel.htb`.
- La web es una aplicación Node.js con login y una sección `/dev`.
- `/.git/HEAD` es accesible y el repositorio contiene el código fuente.

## Enumeración

- `git-dumper http://vessel.htb/.git ./src` reconstruye la aplicación.
- El login usa `mysqljs` y compara `password` con el valor de la base; un objeto anidado altera la consulta.
- El código incluye credenciales de OWA y la ruta de un backup PDF.

## Foothold

Se envía `username=admin&password[password]=1` para saltar la comparación y entrar al panel. Allí se explota OWA 1.7.3 con CVE-2022-24637 para escribir un PHP y obtener una shell como `www-data`.

```bash
curl -d 'username=admin&password[password]=1' http://vessel.htb/login
python3 CVE-2022-24637.py http://vessel.htb/owa/
# webshell en /owa/data/... y reverse shell
```

## Movimiento lateral

La shell permite leer un binario PyInstaller y un PDF protegido. Se extrae el código con `pyinstxtractor` y se rompe el PDF con `pdfcrack`; las credenciales resultantes sirven para SSH como `steve`.

## Escalada de privilegios

`pinns` tiene SUID y es vulnerable a CVE-2022-0811: permite manipular `core_pattern` y ejecutar un programa cuando un proceso falla. Se prepara un core handler que copia `/bin/bash` con SUID y se provoca un crash.

```bash
find / -perm -4000 -type f 2>/dev/null
# pinns -d ... con el payload de CVE-2022-0811
cat /proc/sys/kernel/core_pattern
```

## Evidencia

- Código reconstruido desde `/.git`.
- Login con `password[password]=1` y webshell en OWA.
- Credenciales de `steve` y `pinns` SUID explotado.

## Lecciones aprendidas

- Un `.git` expuesto revela el código y las credenciales de la aplicación.
- La coerción de tipos en un driver puede convertir un objeto en una condición verdadera.
- Un SUID de CRI-O mal configurado permite escapar del contenedor o elevar privilegios.

## Mitigación y detección

- Bloquear `/.git` y no desplegar el repositorio en el webroot.
- Validar tipos y usar consultas parametrizadas en el login.
- Actualizar CRI-O/pinns y revisar binarios SUID innecesarios.

## Referencias

- [0xdf — Vessel](https://0xdf.gitlab.io/2023/03/25/htb-vessel.html)
- [IppSec — Vessel](https://www.youtube.com/watch?v=ZANv0DlrTN8)
- [Hack The Box — Vessel](https://app.hackthebox.com/machines/vessel)
