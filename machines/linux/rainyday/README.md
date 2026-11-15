---
machine: RainyDay
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, idor, docker, flask, jail-escape, use-after-free, unicode, privesc]
---

# RainyDay — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un IDOR filtra hashes; se crackea el de `gary` y se entra a un gestor de contenedores. Desde un contenedor se alcanza una API de desarrollo que aplica regex a archivos y se convierte en lectura arbitraria; se filtra la clave Flask, se forja la sesión de `jack` y se escapa de la jaula para leer su clave SSH. En el host, un use-after-free en Python da `jack_adm`, y un programa de hash con truncamiento Unicode permite adivinar el salt y romper la contraseña de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH y `80` nginx con `rainyday.htb`.
- `ffuf` descubre `rainycloud.htb` y `dev.rainycloud.htb`.
- La web principal es una empresa de contenedores cloud.

## Enumeración

- Un IDOR en la API devuelve los hashes de `jack` y `gary`.
- `gary` se crackea con `john`; su cuenta accede al panel de contenedores.
- Se crea un contenedor `alpine-python` y se obtiene una shell en él.

```bash
john --wordlist=rockyou.txt hashes.txt
```

## Foothold

Desde el contenedor se alcanza la API de desarrollo, que aplica una regex a un archivo. Se construye un script Python que convierte la respuesta en lectura arbitraria y se lee el código de Flask para obtener la `SECRET_KEY`.

```bash
flask-unsign --unsign --cookie '<COOKIE>' -w <(echo '<SECRET>')
```

## Movimiento lateral

Con la clave se firma una cookie como `jack` y se accede a su contenedor `secrets`. La jaula comparte el filesystem del host y un symlink en `cwd` apunta a `/home/jack`; se lee la clave SSH privada y se entra al host.

```bash
flask-unsign --sign --cookie "{'username': 'jack'}" --secret <SECRET>
ssh -i jack_key jack@rainyday.htb
```

## Escalada de privilegios

En el host, `safe_python` es SUID y tiene un use-after-free. El exploit da una shell como `jack`, y ejecutado con `safe_python` da `jack_adm`. Este puede ejecutar `hash_password.py` como root; el programa trunca la entrada Unicode y usa un salt secreto. Se genera una lista de contraseñas y se fuerza el salt hasta coincidir con el hash de root.

```bash
./exploit
sudo /usr/bin/safe_python ./exploit
python3 brute_salt.py
```

## Evidencia

- IDOR y hashes de `jack`/`gary`.
- Contenedor y API de desarrollo con lectura arbitraria.
- `SECRET_KEY` de Flask y cookie de `jack`.
- Escape de la jaula y clave SSH.
- Use-after-free, truncamiento Unicode y root.

## Lecciones aprendidas

- Un IDOR en una API puede filtrar todos los hashes.
- Las APIs de desarrollo con regex son lectura de archivos.
- La jaula de un contenedor no aísla si comparte el filesystem.
- Los programas SUID y el manejo de Unicode amplían la escalada.

## Mitigación y detección

- Autorizar cada objeto y no devolver hashes.
- Retirar APIs de desarrollo y validar rutas.
- Aislar contenedores con namespaces y montajes mínimos.
- Revisar binarios SUID y normalizar Unicode antes de hashear.

## Referencias

- [0xdf — RainyDay](https://0xdf.gitlab.io/2023/02/18/htb-rainyday.html)
- [IppSec — RainyDay](https://www.youtube.com/watch?v=E5TOeiCnGkE)
- [Hack The Box — RainyDay](https://app.hackthebox.com/machines/rainyday)
