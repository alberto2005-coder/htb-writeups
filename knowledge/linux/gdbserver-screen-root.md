---
topic: gdbserver y screen — ejecución y sesión de root
tags: [linux, gdbserver, screen, debugging, privesc]
---

# gdbserver y screen — ejecución y sesión de root

[🌐 English](gdbserver-screen-root.en.md) | **Español**

## Concepto

`gdbserver` permite adjuntarse a un proceso y ejecutar funciones en su contexto. Si escucha en loopback pero es alcanzable desde una aplicación vulnerable, se convierte en ejecución de código. Una sesión `screen` multiusuario de root permite adjuntarse sin credenciales y obtener su shell.

## Cuándo aplica

- `/proc/net/tcp` o un escaneo local revela `gdbserver`.
- La aplicación vulnerable permite SSRF o lectura de `/proc`.
- Root mantiene una sesión `screen` con multiusuario.

## Procedimiento

1. Enumerar procesos y sockets desde `/proc`.
2. Alcanzar `gdbserver` y adjuntarse al proceso.
3. Ejecutar un comando con `call system`.
4. Buscar sesiones `screen` y adjuntarse a la de root.

## Comandos

```bash
cat /proc/net/tcp
ps aux | grep -i gdb
gdb -q -ex "target remote 127.0.0.1:1337" -ex "call system(\"id\")"
screen -ls
screen -x root/root
```

## Variantes

- Usar `gdbserver --attach` sobre un proceso privilegiado.
- Combinar con un túnel SSH o un proxy para alcanzar loopback.
- Aprovechar `screen` con `-x` o `-r` si el multiusuario está activo.

## Limitaciones

- `gdbserver` debe aceptar la conexión y el proceso debe ser depurable.
- La sesión `screen` puede requerir el mismo usuario o multiusuario.
- SELinux/AppArmor pueden bloquear `ptrace`.

## Mitigación

- No exponer `gdbserver` y eliminarlo de producción.
- Deshabilitar multiusuario en `screen` y cerrar sesiones de root.
- Restringir `ptrace` y la lectura de `/proc` desde la aplicación.

## Detección

- Conexiones a puertos de `gdbserver`.
- `ptrace` o `call system` desde procesos de depuración.
- Sesiones `screen` de root abiertas y adjunciones inusuales.

## Referencias

- [0xdf — Backdoor](https://0xdf.gitlab.io/2022/04/23/htb-backdoor.html)
- [GNU Screen — manual](https://www.gnu.org/software/screen/manual/screen.html)
- [GDB — Remote debugging](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Remote-Debugging.html)
