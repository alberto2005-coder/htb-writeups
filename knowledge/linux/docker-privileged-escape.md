---
topic: Docker privileged escape
tags: [linux, docker, privileged, container-escape, sudo, mount]
---

# Docker privileged escape

[🌐 English](docker-privileged-escape.en.md) | **Español**

## Concepto

Un contenedor ejecutado con `--privileged` recibe capacidades amplias y acceso a dispositivos del host. Si un usuario puede lanzar `docker exec --privileged` mediante `sudo`, puede montar el disco del host y modificar archivos fuera del contenedor, incluido `/etc/sudoers`.

## Cuándo aplica

- Reglas `sudo` que permiten `docker exec` o `docker run`.
- Contenedores privilegiados ya en ejecución.
- Acceso al socket de Docker.
- Host con el disco montado o accesible como dispositivo de bloque.

## Procedimiento

1. Revisar `sudo -l` y los contenedores disponibles.
2. Confirmar que el contenedor es privilegiado.
3. Identificar la partición del host con `lsblk` o `fdisk -l`.
4. Montarla dentro del contenedor.
5. Escribir en `/etc/sudoers` o extraer credenciales.

```bash
sudo -l
sudo docker ps
sudo docker exec --privileged <CONTAINER> sh -c 'lsblk; mount /dev/sda1 /mnt; cat /mnt/etc/shadow'
sudo docker exec --privileged <CONTAINER> sh -c 'echo "<USER> ALL=(ALL) NOPASSWD:ALL" >> /mnt/etc/sudoers'
```

## Variantes

- Montaje del socket `/var/run/docker.sock`.
- `docker run -v /:/mnt --privileged` para montar la raíz.
- Abuso de `--pid=host` o `--net=host`.
- Escape mediante `nsenter` si se comparte el namespace.

## Limitaciones

- El montaje puede requerir el nombre correcto del dispositivo.
- SELinux o AppArmor pueden bloquear la escritura.
- El contenedor debe seguir en ejecución.
- Una regla `sudo` limitada a un contenedor concreto reduce el alcance.

## Mitigación y detección

- No conceder `docker` ni `docker exec` a usuarios no administradores.
- Evitar `--privileged` y montajes del host.
- Usar rootless Docker o pods sin capacidades.
- Auditar comandos `docker` con `sudo`, montajes y escrituras en `/etc/sudoers`.

## Referencias

- <https://docs.docker.com/engine/security/>
- <https://attack.mitre.org/techniques/T1611/>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/docker-breakout-privilege-escalation.html>
