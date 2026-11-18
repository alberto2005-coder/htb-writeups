---
machine: Awkward
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, api, jwt, ssrf, file-read, symlink, privesc]
---

# Awkward — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

`hat-valley.htb` aloja una tienda en el vhost `store.hat-valley.htb`. El portal de la tienda solo comprueba que la cookie de sesión valga `guest`; cambiarla por cualquier otro valor da acceso a `/dashboard`. Desde ahí, `/api/store-status` acepta una URL y hace una petición desde el servidor (SSRF), y `/api/staff-details` devuelve usuarios y hashes que se crackean con `hashcat`. El SSRF alcanza la documentación interna de la API, donde se descubre una inyección `awk` que permite leer archivos y un JWT cuyo secreto se crackea para firmar peticiones. Con el file read se localiza un backup, se descarga y se extrae con `xpad`, y de su configuración sale la contraseña de SSH de `bean`. Para root se abusa otra vez de la tienda: un carrito convertido en symlink escribe en `leave_requests.csv`, y el correo que root procesa con ese contenido ejecuta la inyección de comandos.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.9p1 Ubuntu 3.
- `80` nginx 1.18.0 (Ubuntu).
- Sin otros puertos abiertos.

```bash
ffuf -u http://hat-valley.htb -H "Host: FUZZ.hat-valley.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

El vhost `store.hat-valley.htb` aparece al fuzzear. Se añade junto al principal a `/etc/hosts`.

## Enumeración

La web principal es una página corporativa con enlaces a la tienda. `store.hat-valley.htb` pide autenticación para `/hr`, pero el código solo redirige cuando la cookie de sesión vale `guest`:

```text
Cookie: session=guest  ->  redirect a /hr
Cookie: session=<CUALQUIER OTRO VALOR>  ->  /dashboard
```

Con la cookie modificada se accede al panel. El botón de estado genera:

```http
GET /api/store-status?url=%22http://store.hat-valley.htb%22
```

y la respuesta confirma que el servidor consulta la URL indicada. Apuntando a `http://127.0.0.1:<PUERTO>` se alcanza un servicio interno con la documentación de la API.

`/api/staff-details` no exige autenticación y devuelve las cuentas con sus hashes:

```bash
curl -s http://hat-valley.htb/api/staff-details | jq -r '.[] | .username + ":" + .password' > hashes
hashcat -m 1400 hashes /usr/share/wordlists/rockyou.txt
```

Las contraseñas crackeadas permiten iniciar sesión como `christopher.jones`, que tiene más permisos en la tienda.

## Foothold

La documentación interna describe un endpoint que ejecuta `awk` con un parámetro controlado por el usuario. Escapando la expresión se consigue ejecutar comandos y leer archivos del servidor. Para las rutas que exigen un JWT, se captura un token y se crackea su secreto HMAC:

```bash
hashcat -m 16500 token.txt /usr/share/wordlists/rockyou.txt
```

Con el secreto se firman tokens válidos y se enumeran rutas y archivos. El file read localiza un backup de la aplicación; se descarga y se extrae:

```bash
wget http://hat-valley.htb/<RUTA>/backup.tar.gz
tar -xzf backup.tar.gz
```

El archivo está protegido con contraseña. `xpad` (o `john` sobre el formato correspondiente) la recupera, y dentro aparece la contraseña de SSH de `bean`:

```bash
ssh bean@hat-valley.htb
```

## Movimiento lateral

La shell de `bean` es local. En su home no hay nada relevante, pero pertenece al grupo que puede escribir en `/var/www/store`, y `/home` contiene el directorio de `christine`, que recibe los correos de la aplicación. No hay un pivote a otra red: el siguiente paso es escalar en el mismo host.

## Escalada de privilegios

Root ejecuta un proceso que lee `/var/www/private/leave_requests.csv` y envía un correo con las solicitudes de ausencia. `bean` no puede escribir el CSV, pero sí el directorio de carritos:

```bash
ln -sf /var/www/private/leave_requests.csv /var/www/store/cart/<UUID>
```

Al añadir un producto al carrito, la aplicación escribe en el archivo enlazado. Se construye un producto cuya primera línea contiene una inyección de comandos; cuando el proceso de root genera el correo, el contenido pasa a la línea de comandos y se ejecuta:

```text
nombre,apellido,fecha,motivo
; <COMANDO> ;
```

El comando lanza una shell como root. El punto clave es que la inyección no se ejecuta en la web, sino en el proceso privilegiado que consume el CSV.

## Evidencia

- Cookie de sesión con valor distinto de `guest` y acceso a `/dashboard`.
- Petición SSRF a `127.0.0.1` con la documentación interna.
- Hashes de `/api/staff-details` crackeados.
- Secreto JWT recuperado y token firmado a mano.
- Backup extraído con `xpad` y contraseña de `bean`.
- Symlink del carrito hacia `leave_requests.csv` y shell de root.

## Lecciones aprendidas

- Una comprobación de autenticación basada en el valor de una cookie del cliente no autentica nada.
- El SSRF convierte un servicio interno sin exponer en la superficie de ataque.
- Un `awk` que interpola entrada del usuario es una vía directa de ejecución y lectura.
- Los JWT con secretos débiles se pueden firmar de nuevo.
- Los flujos asíncronos (correo, colas, cron) heredan los datos del usuario y pueden ejecutarlos con más privilegios.

## Mitigaciones y detección

- Validar la sesión en el servidor con un identificador opaco y firmado; no confiar en valores del cliente.
- Restringir las salidas HTTP del servidor a una lista de destinos y bloquear `localhost` y rangos internos.
- No pasar entrada del usuario a `awk`, `sed` o `sh`; usar APIs del lenguaje y listas de permitidos.
- Firmar los JWT con secretos largos y rotarlos; rechazar tokens con algoritmos no esperados.
- Escribir los CSVs con permisos del proceso y sanear el contenido antes de usarlo en un correo.
- Alertar de symlinks en directorios de subida y de procesos de correo que lanzan comandos.

## Referencias

- [0xdf — Awkward](https://0xdf.gitlab.io/2023/02/25/htb-awkward.html)
- [IppSec — Awkward](https://www.youtube.com/watch?v=gmaizI5Xcqs)
- [Hack The Box — Awkward](https://app.hackthebox.com/machines/awkward)
