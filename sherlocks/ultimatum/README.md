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

2. **Vector**: **CVE-2023-3460** en el plugin **Ultimate Member < 2.6.7**. El fallo permite a un visitante sin cuenta crear un administrador de WordPress abusando de los campos de registro; el PoC público deja un usuario llamado **`secragon`**, y ese nombre es la firma que aparece en los logs del Sherlock.

```bash
grep -r "Version:" wp-content/plugins/<plugin>/ | sort -u
```

3. **Ejecución**: tras el admin falso, el atacante navega el panel, instala un **web shell** y abre una shell remota; en `wp-content/uploads` y en los temas aparecen los ficheros nuevos, y el `access.log` muestra el `POST` de creación de cuenta seguido de actividad administrativa.

4. **Persistencia**: usuario admin nuevo en la base, `mu-plugins`, temas modificados y tareas cron de WP.

```bash
wp user list --role=administrator
```

5. **Restauración**: reponer el plugin y el core desde el paquete oficial, rotar credenciales, y revisar `wp-config.php` por modificaciones.

## Conclusiones

- Acceso inicial con **CVE-2023-3460**: el PoC crea el administrador `secragon` sin autenticarse, y ese nombre queda en el `access.log`.
- Tras el admin falso, exploración manual del panel, instalación de un **web shell** y shell remota desde el propio servidor.
- Alcance: ficheros nuevos en `wp-content`, usuarios añadidos y cron de WordPress; la restauración exige limpiar todo eso, no solo borrar el admin.

## Lecciones

- El nombre del usuario creado por el PoC (`secragon`) es la firma que enlaza el exploit con el resto de la actividad.
- Un plugin con CVE de escalada de privilegios no necesita shell para ser crítico: crea un admin y desde ahí se opera.
- Comparar la lista de plugins y sus versiones con la fecha del primer `POST` sospechoso fecha el compromiso.

## Qué enseña

- El `access.log` cuenta el orden de los hechos: escaneo, exploit y subida.
- Un plugin sin actualizar es el vector más común en WordPress.
- Restaurar no es sólo volver a la copia: hay que rotar credenciales y revisar persistencia.

## Tropiezos

- **Tráfico mezclado**: separar peticiones legítimas (bots, feeds) por *user-agent* y hora.
- **Ficheros ofuscados**: un `functions.php` alterado puede pasar desapercibido; comparar con el original.
- **Caché**: si hay CDN, parte del ataque puede no aparecer en el log del origen.
