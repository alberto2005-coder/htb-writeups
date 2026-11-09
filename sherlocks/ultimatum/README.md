---
sherlock: Ultimatum
domain: DFIR / Web
difficulty: Easy
platform: Hack The Box
evidence: Logs y ficheros de un WordPress comprometido
tools: [grep, access.log, WP-CLI, diff]
state: Retired
tags: [dfir, dfir-/-web]
---


# Ultimatum — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Un blog **WordPress** deja de funcionar bien y el equipo sospecha de un plugin. Se entregan los registros y los ficheros del sitio para identificar el vector, el alcance y cómo restaurarlo.

## Evidencias

- Logs del servidor web (access/error) y una copia del árbol del WordPress.

## Investigación

1. **Cuándo empezó**: ordenar el `access.log` por hora y buscar ráfagas de peticiones a un mismo plugin.

```bash
awk '{print $4, $7}' access.log | sort | uniq -c | sort -rn | head
grep -i 'wp-content/plugins' access.log | awk '{print $7}' | sort | uniq -c | sort -rn
```

2. **Vector**: un plugin desactualizado con una ruta vulnerable (`admin-ajax.php?action=...`, subida o LFI). Comparar con la versión publicada.

```bash
grep -r "Version:" wp-content/plugins/<plugin>/ | sort -u
```

3. **Ejecución**: peticiones POST al endpoint vulnerable y respuestas 200 inusuales; tras ellas aparecen ficheros nuevos en `wp-content/uploads`.

4. **Persistencia**: usuario admin nuevo en la base, `mu-plugins`, temas modificados y tareas cron de WP.

```bash
wp user list --role=administrator
```

5. **Restauración**: reponer el plugin y el core desde el paquete oficial, rotar credenciales, y revisar `wp-config.php` por modificaciones.

## Conclusiones

[🇬🇧 English](README.en.md) | **Español**

## Lecciones

- Qué se probó y falló, y qué harías distinto la próxima vez.

## Qué enseña

- El `access.log` cuenta el orden de los hechos: escaneo, exploit y subida.
- Un plugin sin actualizar es el vector más común en WordPress.
- Restaurar no es sólo volver a la copia: hay que rotar credenciales y revisar persistencia.

## Tropiezos

- **Tráfico mezclado**: separar peticiones legítimas (bots, feeds) por *user-agent* y hora.
- **Ficheros ofuscados**: un `functions.php` alterado puede pasar desapercibido; comparar con el original.
- **Caché**: si hay CDN, parte del ataque puede no aparecer en el log del origen.
