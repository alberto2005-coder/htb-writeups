---
machine: Catch
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, android, apk, gitea, lets-chat, credentials]
---

# Catch — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Una aplicación Android deja una API y credenciales en el APK. El análisis estático revela un Gitea y un Let's Chat internos; las credenciales permiten entrar y escalar por la configuración del servicio. La cadena termina con acceso root mediante una tarea o un binario mal configurado.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,3000,5000 <IP>
```

- SSH, HTTP, Gitea y un servicio de chat.
- La web distribuye un APK.
- Hay vhosts y una API documentada.

## Enumeración

- Se descarga el APK y se descompila con `apktool`/`jadx`.
- `strings` y el manifest revelan URLs, claves y endpoints.
- Gitea expone repositorios; Let's Chat guarda mensajes y credenciales.
- La configuración de la aplicación incluye un usuario con privilegios.

## Foothold

Se usan las credenciales del APK para entrar en Gitea y revisar repositorios. Un repositorio contiene la configuración de Let's Chat o una clave SSH; con ella se accede al host.

```bash
apktool d app.apk
jadx-gui app.apk
curl -s http://<IP>:3000/api/v1/repos/search
```

## Escalada de privilegios

La configuración de Let's Chat o un script de despliegue contiene credenciales de un usuario con `sudo`. Se revisa `sudo -l` y se abusa de una regla de edición o de un servicio para obtener root.

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
```

## Evidencia

- APK descompilado y endpoints extraídos.
- Acceso a Gitea/Let's Chat.
- Credenciales de SSH o de un servicio.
- Regla `sudo` explotada y root.

## Lecciones aprendidas

- Un APK es código y configuración, no solo una app.
- Los secretos embebidos se reutilizan en servicios internos.
- Gitea y los chats suelen contener credenciales y CI.
- Las reglas `sudo` se descubren después del acceso inicial.

## Mitigaciones y detección

- No embeder secretos en aplicaciones móviles.
- Rotar credenciales y usar almacenes de secretos.
- Restringir Gitea/Let's Chat a la red interna y auditar accesos.
- Revisar `sudo` y separar cuentas de despliegue.
- Referencias: OWASP MASVS, Gitea security, HTB Catch.

## Referencias

- <https://www.hackthebox.com/machines/Catch>
- <https://owasp.org/www-project-mobile-app-security/>
- <https://attack.mitre.org/techniques/T1552/>
- <https://attack.mitre.org/techniques/T1548/003/>
