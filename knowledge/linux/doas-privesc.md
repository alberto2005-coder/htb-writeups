---
topic: doas — revisión y abuso de reglas
tags: [linux, openbsd, doas, privesc, sudo]
---

# doas — revisión y abuso de reglas

[🌐 English](doas-privesc.en.md) | **Español**

## Concepto

`doas` ejecuta comandos como otro usuario según `/etc/doas.conf`. Reglas demasiado amplias, `nopass`, `setenv` o binarios que permiten escapar de la shell convierten una delegación legítima en root.

## Cuándo aplica

- `/etc/doas.conf` con `permit nopass` para un binario.
- Usuarios que pueden editar el fichero de configuración.
- Comandos como `vim`, `less`, `find`, `ssh-keygen` o `sh`.

## Procedimiento

1. Leer `/etc/doas.conf` y comprobar la versión.
2. Ejecutar `doas -C /etc/doas.conf` para validar reglas.
3. Identificar comandos permitidos y sus opciones de escape.
4. Ejecutar una shell o escribir un fichero privilegiado.
5. Confirmar el UID resultante.

## Comandos

```bash
cat /etc/doas.conf
doas -C /etc/doas.conf
doas -l
doas <COMMAND>
```

## Variantes

- `doas vim` y `:!sh`.
- `doas ssh-keygen` para firmar una clave.
- `doas.conf` escribible por el usuario.

## Limitaciones

- La regla puede limitar argumentos y usuarios.
- `doas` puede no estar instalado.
- El binario debe conservar una vía de escape.

## Mitigación

- Limitar `doas` a comandos y argumentos concretos.
- Evitar `nopass` y `setenv`.
- Proteger `/etc/doas.conf` y auditar cambios.

## Detección

- Ejecuciones `doas` desde procesos no interactivos.
- Shells hijas de binarios delegados y cambios en `doas.conf`.

## Referencias

- <https://man.openbsd.org/doas.conf>
- <https://attack.mitre.org/techniques/T1548/>
