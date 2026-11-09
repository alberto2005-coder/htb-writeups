---
sherlock: Bumblebee
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, phpbb, sqlite, access-log, web-shell, credential-theft]
---

# Bumblebee — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin respuestas literales de la plataforma.

## Escenario

Un contratista externo entró en el foro interno de la empresa por la wifi de invitados y, al parecer, se llevó las credenciales de un administrador. Solo hay dos evidencias: la base de datos SQLite del foro (phpBB) y el `access.log` del servidor web.

## Evidencias

```text
incident.tgz
├── phpbb.sqlite3
└── access.log
```

## Investigación

### 1. Inventario de la base de datos

```bash
sqlite3 phpbb.sqlite3 ".tables"
sqlite3 phpbb.sqlite3 ".schema phpbb_users"
```

Tablas relevantes: `phpbb_users`, `phpbb_posts`, `phpbb_topics`, `phpbb_log`, `phpbb_sessions`. Se ordenan los usuarios por fecha de alta para localizar la cuenta del contratista y se mira su IP de registro (columna `user_ip`).

```bash
sqlite3 -header -column phpbb.sqlite3 \
  "SELECT user_id, username, user_ip, user_regdate FROM phpbb_users ORDER BY user_regdate;"
```

### 2. El post malicioso

Se revisan los mensajes del usuario sospechoso y se busca HTML/JS o un enlace externo:

```bash
sqlite3 phpbb.sqlite3 "SELECT post_id, poster_id, post_time, post_text FROM phpbb_posts WHERE poster_id=<id>;"
```

El patrón es un post con una imagen o enlace que incluye credenciales en la URL o un formulario falso: cuando el administrador lo abre, su navegador envía usuario y contraseña al servidor del atacante.

### 3. Cruce con el access log

```bash
grep '<ip_contratista>' access.log | head
grep -i 'POST /ucp.php' access.log | head
```

Se buscan peticiones `POST` a `ucp.php?mode=login` desde la IP del contratista después del post, y un `200` de sesión válida. También peticiones al `download/file.php` o al panel de administración (`adm/index.php`) para confirmar la escalada de privilegios.

### 4. Escalada y exfiltración

Con la cuenta de admin, el atacante sube su propio usuario a administrador (o crea uno), y luego exporta la base de datos:

```bash
grep -E 'adm/index.php.*(mode=.*user|action=.*)' access.log
grep -i 'backup\|\.sql\|\.sqlite' access.log
```

La combinación de `POST` de login, cambio de grupo y descarga de copia de seguridad cierra la cadena.

## Conclusiones

- Entrada: cuenta creada desde la wifi de invitados, sin verificación de correo.
- Movimiento: post con phishing de credenciales dirigido al administrador.
- Resultado: toma de la cuenta admin, autoascenso y exportación de la base de datos.
- Técnica MITRE: T1566 (phishing), T1078 (cuentas válidas), T1005/T1567 (recopilación y exfiltración).

## Lecciones

- Un foro con registro abierto y sin moderación de enlaces es una plataforma de phishing interna.
- El `access.log` es la prueba que convierte «un post raro» en una cronología: IP, hora, endpoint y código de respuesta.
- En phpBB, vigilar cambios de grupo (`phpbb_user_group`) y descargas de backup; el admin legítimo no las hace a diario.
