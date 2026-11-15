---
machine: Mango
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, nosql, mongodb, sudo, jjs]
---

# Mango — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El vhost `staging-order.mango.htb` usa MongoDB y acepta operadores en el login. Un bypass con `[$ne]` da acceso y un `$regex` extrae usuario y contraseña carácter a carácter. Esa contraseña se reutiliza por SSH para `mango` y `admin`, y un `jjs` con SUID permite leer archivos y escribir una clave en `authorized_keys` de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 18.04.
- `80/tcp` devuelve `403`; `443/tcp` sirve una web y un certificado con `staging-order.mango.htb`.
- El vhost de staging es la aplicación real; el resto es una landing.

## Enumeración

- El login envía `username`, `password` y `login` por `POST`.
- `username[$ne]=x&password[$ne]=x` redirige a `/home.php`, lo que confirma la inyección NoSQL.
- El campo `password[$regex]` permite comparar prefijos y extraer el valor completo.

## Foothold

Se automatiza la extracción con `$regex` para `admin` y se obtiene su contraseña. También se enumeran otros usuarios de la base. La contraseña funciona por SSH para `mango`; `admin` no acepta SSH por `AllowUsers`, pero se puede usar `su`.

```python
import requests, string
for c in string.printable:
    r = requests.post('http://staging-order.mango.htb/',
        data={'username':'admin','password[$regex]':'^'+prefix+c+'.*','login':'login'})
```

## Movimiento lateral

`mango` y `admin` comparten la contraseña extraída de la base. `mango` entra por SSH y `admin` se alcanza con `su`, lo que da acceso a la flag de usuario y a un segundo contexto para enumerar SUID.

## Escalada de privilegios

`/usr/lib/jvm/java-11-openjdk-amd64/bin/jjs` es SUID y pertenece al grupo `admin`. Con Nashorn se lee `/root/root.txt` o se escribe una clave pública en `/root/.ssh/authorized_keys`.

```bash
/usr/lib/jvm/java-11-openjdk-amd64/bin/jjs
jjs> var FileWriter = Java.type("java.io.FileWriter");
jjs> var fw = new FileWriter("/root/.ssh/authorized_keys");
jjs> fw.write("<PUBLIC_KEY>");
jjs> fw.close();
```

## Evidencia

- Redirección a `/home.php` con `[$ne]`.
- Contraseña extraída con `$regex` y sesión SSH como `mango`.
- `jjs` SUID y acceso como root.

## Lecciones aprendidas

- Pasar arrays a un driver NoSQL cambia la semántica de la consulta.
- Los errores de autenticación uniformes no impiden un oráculo booleano.
- Un intérprete SUID como `jjs` es una vía directa a lectura y escritura privilegiada.

## Mitigación y detección

- Validar que usuario y contraseña sean cadenas y no objetos.
- Usar consultas parametrizadas y limitar operadores aceptados.
- Eliminar SUID innecesarios y restringir intérpretes de scripting.

## Referencias

- [0xdf — Mango](https://0xdf.gitlab.io/2020/04/18/htb-mango.html)
- [IppSec — Mango](https://www.youtube.com/watch?v=NO_lsfhQK_s)
- [Hack The Box — Mango](https://app.hackthebox.com/machines/mango)
