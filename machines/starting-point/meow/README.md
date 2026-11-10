---
machine: Meow
os: Linux
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/394
category: Starting Point
state: Available
pwned: 2026-11-05
tags: [telnet, ftp, misconfiguration]
---

# Meow — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Linux · Very Easy

## TL;DR

La máquina expone **Telnet (23/tcp)** y permite iniciar sesión como `root` **sin contraseña**. En menos de un minuto se obtiene una shell de root y la flag.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

Resultado relevante:

```text
PORT   STATE SERVICE VERSION
23/tcp open  telnet  Linux telnetd
```

- Solo hay un puerto abierto: **23/tcp (Telnet)**.
- No hay HTTP, SSH ni SMB. El servicio Telnet es la única superficie de ataque.
- `nmap -sV` identifica un `telnetd` de Linux (típico de imágenes de laboratorio).

## Enumeración

Telnet es un protocolo de texto plano. Antes de intentar fuerza bruta, lo primero es comprobar si acepta **credenciales por defecto o vacías**:

```bash
telnet <TARGET_IP>
```

El servidor pide login:

```text
login: root
Password:
```

Al dejar la contraseña vacía (solo `Enter`), la autenticación se acepta.

## Foothold

```bash
telnet <TARGET_IP>
# login: root
# Password: <Enter>

id
cat /root/flag.txt
```

```text
uid=0(root) gid=0(root) groups=0(root)
<FLAG>
```

No hay explotación: es una **mala configuración**. El servicio Telnet está habilitado y la cuenta `root` no tiene contraseña, por lo que cualquier persona con conectividad de red obtiene control total.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- No aplica: la flag está en el propio servicio comprometido; no hay usuario de sistema que comprometer ni escalada posterior.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Telnet debe tratarse como obsoleto:** transmite credenciales y toda la sesión en texto plano.
- Probar credenciales vacías o por defecto es un paso válido y rápido en entornos de laboratorio (y sigue funcionando en redes reales mal configuradas).
- Enumerar **todos** los puertos es clave: sin el `-p-` podrías no ver el 23.
- La máquina demuestra que la superficie de ataque más pequeña puede ser la más crítica.

## Mitigaciones y detección

**Cómo se corrige:**

- Deshabilitar Telnet y usar **SSH** con autenticación por clave.
- Prohibir cuentas con contraseña vacía (`pam`/`/etc/shadow`).
- Bloquear el acceso directo de `root` por red (`PermitRootLogin no`).
- Segmentar y filtrar la red de gestión.

**Cómo se detectaría:**

- Alertas por conexiones entrantes al puerto 23.
- Reglas de auditoría sobre logins de `root` desde IP remotas.
- Revisión de configuración: `telnetd` instalado/activo sin justificación.

## Referencias

- [OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [CIS Benchmarks — Linux](https://www.cisecurity.org/benchmark/distribution_independent_linux)
- MITRE ATT&CK: [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/), [T1021 Remote Services](https://attack.mitre.org/techniques/T1021/)
