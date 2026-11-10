---
machine: Ignition
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, magento, default-credentials, linux, tier1]
---

# Ignition — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

Un **Magento 2** en **80/tcp** con el vhost `ignition.htb`. El panel `/admin` sigue con credenciales débiles (`admin:qwerty123`): se entra y la flag aparece en el dashboard.

---

## Reconocimiento

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
80/tcp open  http    nginx
```

```bash
echo "<TARGET_IP>    ignition.htb" | sudo tee -a /etc/hosts
```

- Un solo puerto: la web.
- Por IP la página no carga bien: depende del `Host`, así que el vhost es obligatorio.

```bash
whatweb http://ignition.htb
```

```text
Magento, nginx, PHP, cookies de sesión de Magento
```

## Enumeración

```bash
gobuster dir -u http://ignition.htb -w /usr/share/wordlists/dirb/common.txt
```

```text
/admin        (302 → /admin/adminhtml)
/setup        (bloqueado)
/errors
/robots.txt
```

- `/admin` redirige al login del backend (`adminhtml`).
- `/setup` está instalado pero protegido: no se intenta reinstalar.
- No hay catálogo público explotable: el objetivo es el panel.

## Foothold

Magento exige contraseñas de al menos 7 caracteres con letra y número. Se prueban las combinaciones habituales y el patrón que sugiere el propio reto (teclado):

```text
usuario:    admin
contraseña: qwerty123
```

```bash
curl -s -c cookies.txt http://ignition.htb/admin/ -o /dev/null
```

Tras autenticarse en el navegador, el **Dashboard** muestra la flag en el bloque de bienvenida.

Sin shell: la cadena termina en el panel. La vulnerabilidad es de **autenticación**, no de ejecución.

## Movimiento lateral

- No aplica: un solo servicio y ninguna credencial adicional.
- En un Magento real se buscaría el `app/etc/env.php` (credenciales de MySQL) tras obtener ejecución.

## Escalada de privilegios

- No aplica: no hay acceso al sistema operativo.
- Si se hubiera conseguido RCE (extensión maliciosa), el siguiente paso sería el usuario de `nginx`/`www-data`.

## Evidencia

- Captura del login y del dashboard con la flag redactada.
- Sin credenciales reales en el repositorio.

## Lecciones aprendidas

- Un CMS sin parchear no es la única vía: una contraseña débil en el backend basta.
- Las políticas de contraseña (longitud mínima, letra y número) no evitan `qwerty123`.
- `robots.txt` y `/setup` confirman el producto y la versión aunque el panel esté oculto.
- Enumerar el vhost antes de atacar evita perseguir la IP desnuda.

## Mitigaciones y detección

**Cómo se corrige:**

- Contraseñas robustas y únicas, MFA y bloqueo por intentos en el admin.
- Restringir `/admin` por IP o VPN y renombrar la ruta del backend.
- Eliminar `/setup` tras la instalación y mantener Magento parcheado.
- Alertas de login desde ubicaciones nuevas.

**Cómo se detectaría:**

- Serie de `POST /admin/adminhtml` con 302 fallidos seguidos de un 200 (fuerza bruta exitosa).
- Accesos a `/setup` o `robots.txt` desde IPs externas.
- Sesiones administrativas desde ASN no corporativos.

- CWE-1391: Use of Weak Credentials
- OWASP Top 10 2021: A07 Identification and Authentication Failures
- MITRE ATT&CK: [T1078.001 Default Accounts](https://attack.mitre.org/techniques/T1078/001/), [T1110.001 Password Guessing](https://attack.mitre.org/techniques/T1110/001/)

## Referencias

- [Magento — Security best practices](https://experienceleague.adobe.com/docs/commerce-operations/security-and-compliance/security-best-practices.html)
- [OWASP — Credential Stuffing Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html)
