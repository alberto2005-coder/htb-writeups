---
sherlock: dOOMs Day
domain: SOC
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, web, php2shell, cve, webshell, log-analysis]
---


# dOOMs Day — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de investigación; sin respuestas literales de la plataforma.

## Escenario

Una web PHP gestionada por un CMS de terceros aparece con ficheros nuevos y tráfico saliente hacia un host desconocido. Se entrega el árbol web, los logs de acceso y la base de datos del CMS; el objetivo es reconstruir la cadena de explotación de la vulnerabilidad **PHP2Shell** y medir qué se hizo tras el acceso.

## Evidencias

- `access.log` / `error.log` de Apache o nginx.
- Copia del webroot (incluye `.htaccess`, `uploads/`, `cache/`).
- Export de la base de datos con la tabla de plantillas o configuración.
- Opcional: `last`, `auth.log` y reglas de cron del host.

## Investigación

### 1. Encontrar la petición inicial

PHP2Shell se abusa a través de una petición HTTP que inyecta código en un contexto que el CMS evaluará después (plantilla, caché o parámetro serializado). En el log se busca la forma anómala, no el `200` genérico:

```bash
awk '{print $6, $7}' access.log | sort | uniq -c | sort -rn | head -30
grep -E "POST .*(template|cache|theme|module)" access.log | head
```

Un `POST` a un endpoint de administración con un `User-Agent` de script (`python-requests`, `curl`) y cuerpo grande es el candidato. El código de respuesta (200 en lugar de 302/403) confirma que se saltó la autenticación.

### 2. Verificar si el payload se evaluó

```bash
grep -RIn "eval\|assert\|create_function\|preg_replace" webroot/ --include="*.php" | head -40
find webroot/ -newermt "2026-01-01" -type f -printf "%TY-%Tm-%Td %TH:%TM  %p\n" | sort
```

Los ficheros con fecha del incidente en directorios escribibles (`uploads`, `cache`, `tmp`, `sessions`) son el webshell. Un `eval` sobre datos controlables por el usuario en el CMS original explica por qué funcionó.

### 3. Qué hizo el atacante

```bash
grep -E "shell|cmd|upload|wget|curl" access.log | awk '{print $1, $4, $7}' | sort | uniq -c | sort -rn | head
```

Se reconstruye la secuencia: subida del webshell → reconocimiento (`whoami`, `id`, `uname -a`) → descarga de una segunda etapa → movimiento lateral o exfiltración. Las peticiones al webshell con `?cmd=` o `?c=` en el `GET` son la firma.

### 4. Persistencia y alcance

```bash
crontab -l; ls -la /etc/cron.*
grep -RIn "base64_decode\|gzinflate" webroot/ | head
```

Se revisan tareas programadas, usuarios creados (`/etc/passwd` con fechas recientes) y conexiones salientes del periodo. El alcance se cierra con los usuarios del CMS comprometidos: si la inyección llegó desde una cuenta, hay que rotar sus credenciales y la `APP_KEY`.

## Conclusiones

- Acceso por explotación de PHP2Shell en el CMS, sin credenciales válidas.
- Webshell en un directorio de subidas con ejecución PHP habilitada.
- Post-explotación mínima: reconocimiento y una segunda etapa descargada.

## Lecciones

- Un CMS que escribe plantillas o caché en disco y las evalúa es RCE si el directorio no bloquea PHP.
- La diferencia entre compromiso y susto está en `access.log`: hay que leer el cuerpo de la petición, no solo la URL.
- Mitigación: `php_admin_flag engine off` en directorios de subida, WAF con reglas de payload, y actualizar el CMS.
