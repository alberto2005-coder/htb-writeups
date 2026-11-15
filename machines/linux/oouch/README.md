---
machine: Oouch
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, oauth, csrf, uwsgi, dbus]
---

# Oouch — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un flujo OAuth sin validación de `state` permite CSRF y enlazar una cuenta ajena al proveedor. Con acceso a la aplicación se llega a SSH; uWSGI permite pivotar a `www-data` y una inyección en el servicio D-Bus de iptables da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
gobuster dir -u http://oouch.htb -w /usr/share/wordlists/dirb/common.txt
# Flujo OAuth sin state
curl -i "http://oouch.htb/oauth/authorize?client_id=<ID>&redirect_uri=http://<IP>/callback"
# Tras el acceso SSH
ss -lntp
busctl --system list
busctl call <SERVICE> <PATH> <IFACE> <METHOD> s "<PAYLOAD>"
```

## Enumeración

- Aplicación Django y servidor OAuth con flujos de autorización.
- Parámetro `state` predecible o no validado.
- Servicio D-Bus que ejecuta reglas de iptables.

## Acceso inicial

Se inicia el flujo OAuth y se captura el callback. Sin `state` válido, se fuerza a la víctima a enlazar la cuenta del atacante; el token permite entrar a la aplicación y obtener una clave SSH.

## Escalada de privilegios

uWSGI expone un socket con permisos débiles y permite ejecutar código como `www-data`. El servicio D-Bus que gestiona bloqueos de iptables concatena argumentos; se inyecta un comando y se ejecuta como root.

## Evidencia

- Callback OAuth sin validación de `state`.
- Cuenta enlazada y acceso SSH.
- Mensaje D-Bus con inyección y shell de root.

## Lecciones aprendidas

- `state` es la defensa CSRF del flujo OAuth, no un detalle opcional.
- Los sockets de uWSGI pueden ser ejecución remota.
- Un servicio D-Bus que construye comandos de shell es inyección.

## Mitigación y detección

- Validar `state` y usar PKCE; no aceptar callbacks sin sesión.
- Restringir permisos de sockets uWSGI.
- Usar APIs de iptables sin shell y validar argumentos.

## Referencias

- [0xdf — Oouch](https://0xdf.gitlab.io/2020/08/01/htb-oouch.html)
- [OAuth 2.0 — Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [Hack The Box — Oouch](https://app.hackthebox.com/machines/oouch)
