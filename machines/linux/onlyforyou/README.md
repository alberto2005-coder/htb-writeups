---
machine: OnlyForYou
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, lfi, command-injection, neo4j, cypher, pip]
---

# OnlyForYou — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El subdominio `beta` normaliza mal una ruta y permite leer archivos absolutos; con el código de la aplicación principal se descubre una inyección de comandos en el validador de correo. Tras obtener `www-data`, un túnel a Neo4j permite una inyección Cypher que revela el hash de `john`. El usuario puede ejecutar `pip3 download` como root y un paquete malicioso ejecuta `setup.py` con privilegios de root.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH y Nginx.
- `only4you.htb` y `beta.only4you.htb`.
- `ffuf` y `feroxbuster` localizan `/download` y endpoints de formulario.

## Enumeración

- `/download` usa `os.path.join` y un filtro insuficiente de `..`.
- Una ruta absoluta como `/etc/passwd` evade el filtro.
- El código de `form.py` pasa el dominio del correo a `subprocess.run(..., shell=True)`.
- Neo4j escucha en un puerto local y se alcanza con Chisel.

## Foothold

Se lee el código fuente con la ruta absoluta y se inyecta un comando en el campo de correo. El filtro con `re.match` solo ancla el inicio, por lo que un salto de línea o metacaracteres permiten ejecutar `dig` con parámetros adicionales y obtener una reverse shell.

```bash
curl -s "http://beta.only4you.htb/download?file=/var/www/only4you.htb/form.py"
```

## Escalada de privilegios

Con Chisel se accede al panel de Neo4j. Una inyección Cypher en la búsqueda permite volcar usuarios y el hash de `john`, que se crackea. `john` puede ejecutar `pip3 download` como root; se publica un sdist malicioso en el Gogs local y se descarga, ejecutando `setup.py` como root.

```bash
sudo -l
pip3 download --no-deps --no-binary :all: <paquete>
```

## Evidencia

- Lectura de `/etc/passwd` y del código de `form.py`.
- Petición con el campo de correo inyectado y shell como `www-data`.
- Consulta Cypher con el hash de `john`.
- `sudo -l` y ejecución de `setup.py` como root.

## Lecciones aprendidas

- `os.path.join` descarta la base si el segundo argumento es absoluto.
- `re.match` no valida toda la cadena.
- `pip download` de un paquete no confiable ejecuta código durante la construcción.

## Mitigaciones y detección

- Resolver y confinar rutas con `Path.resolve()` y una raíz permitida.
- Parametrizar comandos y evitar `shell=True`.
- Restringir Neo4j a localhost y exigir autenticación.
- No ejecutar `pip` como root sobre índices no confiables.
- Referencias: HTB OnlyForYou, 0xdf, CWE-22/CWE-78.

## Referencias

- <https://www.hackthebox.com/machines/OnlyForYou>
- <https://0xdf.gitlab.io/2023/08/26/htb-onlyforyou.html>
- <https://cwe.mitre.org/data/definitions/78.html>
- <https://attack.mitre.org/techniques/T1059/004/>
