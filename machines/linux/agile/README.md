---
machine: Agile
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, file-read, werkzeug, chrome-debug, sudoedit, cve-2023-22809]
---

# Agile — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una aplicación Flask de gestión de contraseñas tiene una lectura de archivos y el servidor Werkzeug en modo debug. Se obtiene ejecución con el depurador, se extrae una contraseña de la base de datos y se accede por SSH. Una instancia de pruebas con Chrome en modo remoto permite robar la sesión de otro usuario, y `sudoedit` vulnerable a CVE-2023-22809 permite editar un archivo del entorno virtual que root carga al iniciar sesión.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH y Nginx con una aplicación Flask.
- `superpass.htb` y un host de pruebas.
- `feroxbuster` localiza endpoints de descarga y una consola de depuración.

## Enumeración

- La descarga de un archivo acepta una ruta controlada por el usuario.
- Werkzeug está en modo debug y muestra la consola interactiva.
- El código y la base de datos contienen credenciales de usuarios.
- Un proceso de Chrome con puerto de depuración remota pertenece a la instancia de pruebas.

## Foothold

La lectura de archivos permite obtener el código y la configuración. La consola Werkzeug, protegida por el PIN de depuración de Flask, se abre tras calcular o filtrar el PIN; desde ella se ejecutan comandos como el usuario del servicio.

```bash
curl -s "http://superpass.htb/download?file=..."
```

## Escalada de privilegios

Con la contraseña de la base de datos se accede por SSH. El puerto de Chrome debug de la instancia de pruebas permite conectarse, listar pestañas y recuperar cookies o credenciales de la sesión. El segundo usuario puede ejecutar `sudoedit`; CVE-2023-22809 permite añadir archivos arbitrarios a la edición y modificar el entorno virtual que root carga al iniciar sesión.

```bash
sudo -l
sudoedit /etc/hosts /home/<USER>/.venv/lib/python3.*/site-packages/sitecustomize.py
```

## Evidencia

- Respuesta con la ruta leída fuera del directorio permitido.
- Consola Werkzeug y ejecución de `id`.
- Captura del puerto Chrome con pestañas y cookies.
- `sudo -l` mostrando `sudoedit` y ejecución como root.

## Lecciones aprendidas

- El modo debug de Flask nunca debe estar expuesto.
- Un depurador de Chrome sin autenticación es una puerta a sesiones activas.
- CVE-2023-22809 convierte `sudoedit` en escritura arbitraria.

## Mitigaciones y detección

- Desactivar debug y la consola Werkzeug en producción.
- Cerrar puertos de depuración y aislar navegadores de pruebas.
- Actualizar sudo a una versión corregida y limitar `sudoedit` a archivos concretos.
- Referencias: HTB Agile, 0xdf, NVD CVE-2023-22809.

## Referencias

- <https://www.hackthebox.com/machines/Agile>
- <https://0xdf.gitlab.io/2023/08/05/htb-agile.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-22809>
- <https://attack.mitre.org/techniques/T1190/>
