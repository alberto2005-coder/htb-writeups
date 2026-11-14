---
topic: FreeBSD — authpf y anclas pf
tags: [freebsd, pf, authpf, firewall, pivot]
---

# FreeBSD — authpf y anclas pf

[🌐 English](authpf.en.md) | **Español**

## Concepto

`authpf` es una shell de login que activa reglas pf para un usuario autenticado. Si el usuario puede editar su ancla o los ficheros de configuración, puede abrir acceso a redes internas o modificar reglas del cortafuegos.

## Cuándo aplica

- `/etc/pf.conf` con `anchor "authpf/*"`.
- Usuarios cuyo shell es `/usr/sbin/authpf`.
- Anclas o ficheros de authpf con permisos débiles.

## Procedimiento

1. Revisar `/etc/pf.conf`, `/etc/authpf` y el shell del usuario.
2. Comprobar si el usuario puede escribir en el ancla.
3. Iniciar sesión SSH para activar authpf.
4. Añadir reglas para alcanzar la red interna.
5. Verificar con `pfctl -a authpf/<user> -sr`.

## Comandos

```bash
cat /etc/pf.conf
grep authpf /etc/passwd
pfctl -a 'authpf/<USER>' -sr
ssh <USER>@<HOST>
```

## Variantes

- Ficheros `authpf.rules` escribibles.
- Reglas que permiten `rdr` o NAT.
- Reutilización de la sesión para pivoting.

## Limitaciones

- El usuario debe autenticarse correctamente.
- pf debe estar cargado y el ancla habilitada.
- Los permisos pueden impedir la escritura.

## Mitigación

- Restringir la escritura en `/etc/authpf`.
- Revisar las anclas y reglas periódicamente.
- Limitar authpf a usuarios y redes concretas.

## Detección

- Reglas pf nuevas en anclas authpf.
- Sesiones SSH que abren rutas internas.

## Referencias

- <https://man.freebsd.org/cgi/man.cgi?query=authpf>
- <https://docs.freebsd.org/en/books/handbook/firewalls/>
