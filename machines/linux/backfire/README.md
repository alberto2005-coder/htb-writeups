---
machine: Backfire
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, havoc, c2, ssrf, cve-2024-41570, hardhat, jwt, iptables, privesc]
---

# Backfire — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El servidor de archivos de `8000` deja escapar la configuración de un servidor Havoc. La CVE-2024-41570 es un SSRF no autenticado en el manejo de callbacks de los demonios: los comandos `COMMAND_SOCKET` y `COMMAND_PIVOT` se aceptan sin un `RequestID` previo, lo que permite abrir un socket contra el puerto de administración interno de Havoc. Sobre ese socket se habla WebSocket y se alcanza el RCE autenticado, con shell como `ilya`. En su home hay una instalación de HardHatC2 con la configuración por defecto; el secreto JWT por defecto permite forjar un token con rol `Team Lead` y ejecutar comandos como `sergej`. `sergej` puede ejecutar `iptables` e `iptables-save` como root: un comentario con saltos de línea y `iptables-save -f` escriben un archivo arbitrario, lo que permite añadir una clave SSH a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,443,8000,5000,7096 <IP>
```

- `22`: OpenSSH 9.2p1 Debian.
- `443`: nginx 1.22.1, interfaz web.
- `8000`: nginx, servidor de archivos.
- `5000` y `7096`: filtrados desde fuera; se verán desde dentro.

```bash
echo '<IP> backfire.htb' | sudo tee -a /etc/hosts
feroxbuster -k -u https://backfire.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeración

El puerto `443` devuelve un `404` de nginx con la cabecera `X-Havoc`, lo que identifica el producto. El servidor de archivos de `8000` publica documentación y archivos de configuración; entre ellos aparece la configuración del team server de Havoc, con la clave y el listener. Esa fuga es la que permite construir el resto de la cadena.

Dentro del host, `netstat` muestra `40056` (team server, solo en localhost) y `8443` (listener HTTP de Havoc), además de los puertos `5000`/`7096`, que solo aceptan conexiones locales.

## Foothold

La CVE-2024-41570 permite que un demonio falsificado abra un socket en el team server sin autenticarse. Se registra un agente y se envían los comandos `COMMAND_SOCKET` y `COMMAND_PIVOT`, que se aceptan sin comprobar el `RequestID`; el resultado es un túnel hacia `127.0.0.1:40056`. Sobre ese túnel se habla el protocolo WebSocket de Havoc y se usa el RCE autenticado para ejecutar comandos.

```text
Comando 99 (DEMON_INITIALIZE) → registrar agente
COMMAND_SOCKET / COMMAND_PIVOT → abrir túnel al panel interno
WebSocket + comando autenticado → ejecución
```

La shell es de `ilya`.

## Movimiento lateral

En `/home/ilya` hay una nota sobre HardHatC2: `sergej` lo instaló para probar y no cambió los valores por defecto. El proceso corre como `sergej` y el panel escucha en local. El secreto JWT por defecto de HardHatC2 permite forjar un token con rol `Team Lead`; el token se guarda en el almacenamiento local del navegador y con él se accede al panel y se ejecuta un comando, lo que da shell como `sergej`.

## Escalada de privilegios

`sudo -l` muestra dos reglas sin contraseña:

```text
(root) NOPASSWD: /usr/sbin/iptables
(root) NOPASSWD: /usr/sbin/iptables-save
```

`iptables-save` admite `-f <archivo>` para escribir la salida como root. Las reglas permiten incluir un comentario libre; si el comentario contiene saltos de línea, el volcado de `iptables-save` escribe esas líneas en el archivo indicado. Se añade una regla con una clave pública SSH como comentario y se guarda en `/root/.ssh/authorized_keys`:

```bash
sudo iptables -A INPUT -i lo -m comment --comment $'\n<PUBLIC_KEY>\n'
sudo iptables-save -f /root/.ssh/authorized_keys
ssh -i <KEY> root@backfire.htb
```

## Evidencia

- Configuración de Havoc accesible desde el servidor de archivos.
- Túnel abierto contra `127.0.0.1:40056` con los comandos de socket.
- Ejecución de `id` como `ilya`.
- Nota sobre HardHatC2 y proceso corriendo como `sergej`.
- Token con rol `Team Lead` forjado con el secreto por defecto.
- `sudo -l` con `iptables` e `iptables-save`.
- `/root/.ssh/authorized_keys` escrito y sesión SSH como root.

## Lecciones aprendidas

- Un C2 también es software vulnerable y debe parchearse.
- Los comandos de túnel sin comprobación de estado permiten SSRF.
- Los secretos JWT por defecto convierten un panel en una puerta abierta.
- `iptables-save -f` es escritura arbitraria si se controla el contenido de una regla.
- Los comentarios de iptables aceptan saltos de línea y deben filtrarse.

## Mitigaciones y detección

- Actualizar Havoc y revisar los comandos que aceptan callbacks sin autenticación.
- No exponer el panel de administración; separar listeners y management.
- Cambiar todos los secretos por defecto de HardHatC2 y de cualquier C2.
- No conceder `iptables-save` con `sudo`; usar un wrapper que valide destino y contenido.
- Monitorizar escrituras en `/root/.ssh/authorized_keys` y reglas con comentarios multilínea.
- Alertar de conexiones desde el team server hacia puertos internos.

## Referencias

- [0xdf — Backfire](https://0xdf.gitlab.io/2025/06/07/htb-backfire.html)
- [IppSec — Backfire](https://www.youtube.com/watch?v=dZjd4XTms7E)
- [Hack The Box — Backfire](https://app.hackthebox.com/machines/backfire)
- [NVD — CVE-2024-41570](https://nvd.nist.gov/vuln/detail/CVE-2024-41570)
- [Knowledge — SSRF y RCE en Havoc C2](../../../knowledge/web/havoc-ssrf-rce.md)
