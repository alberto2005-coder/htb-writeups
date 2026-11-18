---
topic: KeePass — captura de la contraseña maestra con ptrace
tags: [linux, keepass, kpcli, ptrace, strace, credenciales, mailroom]
---

# KeePass — captura de la contraseña maestra con ptrace

[🌐 English](keepass-ptrace.en.md) | **Español**

## Concepto

Las bases KeePass se cifran con una contraseña maestra y, si se abre desde una consola, esa contraseña se teclea en el terminal del proceso. En Linux, `strace` puede leer las llamadas `read` de otro proceso del mismo usuario y capturar lo que se escribe. En Mailroom, `matthew` abría `personal.kdbx` con `kpcli` y el rastreo del proceso reveló la contraseña maestra, con la que se obtenía la de root.

## Cuándo aplica

- La víctima abre un gestor de contraseñas en el mismo host.
- El atacante tiene una shell como el mismo usuario o como root.
- `kernel.yama.ptrace_scope` permite adjuntarse (0 o 1).
- El gestor lee la contraseña desde la entrada estándar o el terminal.

## Procedimiento

1. Enumerar procesos y localizar el gestor (`kpcli`, `keepassxc-cli`).
2. Confirmar el ámbito de `ptrace`.
3. Adjuntar `strace` al proceso y filtrar `read`.
4. Localizar la contraseña maestra en la salida.
5. Abrir la base con `kpcli` y leer las entradas.
6. Usar la contraseña de root o la clave SSH encontrada.

## Comandos

```bash
ps aux | grep -i keep
cat /proc/sys/kernel/yama/ptrace_scope
strace -f -e trace=read,write -s 200 -p <PID>
```

```bash
kpcli --kdb personal.kdbx
# dentro: ls, cd <grupo>, show -f <entrada>
```

```text
read(0, "<PASSWORD>\n", 4096) = <N>
```

## Variantes

- Volcar la memoria del proceso con `gdb -p` y buscar cadenas.
- Si el gestor usa un socket, interceptar la comunicación con `socat`.
- Con root, leer `/proc/<PID>/mem` o usar `gcore`.
- Combinar con un keylogger si la entrada no pasa por `read`.

## Limitaciones

- `ptrace_scope=2` o `3` impide adjuntarse a procesos de otros usuarios.
- Con `hidepid` no se ven los procesos de la víctima.
- El gestor puede borrar la entrada de la memoria tras usarla.
- Se necesita esperar a que la víctima introduzca la contraseña.

## Mitigación

- Configurar `kernel.yama.ptrace_scope=2` o `3`.
- Usar `hidepid=2` en `/proc` y separar sesiones por usuario.
- Preferir gestores con integración por agente y sin contraseña en terminal.
- Rotar las contraseñas maestras y usar MFA o keyfiles.
- No compartir sesiones ni ejecutar gestores en hosts comprometidos.

## Detección

- Procesos `strace` o `gdb` adjuntos a gestores de contraseñas.
- Lecturas de `/proc/<PID>/mem` por procesos no habituales.
- Eventos de `ptrace` en auditd (`-a always,exit -F arch=b64 -S ptrace`).
- Apertura de bases `.kdbx` desde usuarios distintos del propietario.

## Referencias

- [KeePass — Security](https://keepass.info/help/base/security.html)
- [kpcli](https://github.com/soremwar/kpcli)
- [Linux — Yama ptrace](https://www.kernel.org/doc/html/latest/admin-guide/LSM/Yama.html)
- [0xdf — Mailroom](https://0xdf.gitlab.io/2023/08/19/htb-mailroom.html)
- [Ficha Mailroom](../../machines/linux/mailroom/README.md)
