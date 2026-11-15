---
machine: Spectra
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, wordpress, plugin, initctl, chromeos]
---

# Spectra — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web conduce a WordPress y el panel permite instalar o modificar un plugin para obtener RCE. Un archivo de auto-login da acceso a otro usuario; `initctl` con sudo permite lanzar un trabajo como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443 <IP>
wpscan --url http://spectra.htb --enumerate u,vp
# Panel de WordPress: editar plugin con webshell
curl -s http://spectra.htb/wp-content/plugins/<PLUGIN>/shell.php?cmd=id
# Auto-login
find / -name "*autologin*" 2>/dev/null
cat /opt/autologin
sudo -l
sudo initctl start <JOB>
```

## Enumeración

- WordPress con panel de administración accesible.
- Plugins editables y una cuenta con privilegios.
- `initctl` disponible con sudo en un entorno tipo ChromeOS.

## Acceso inicial

Se enumeran usuarios y plugins; con credenciales del panel se añade un plugin con una webshell o se edita uno existente. Al visitar el plugin se ejecuta código como `nginx` o `www-data`.

## Escalada de privilegios

Un archivo de auto-login contiene credenciales de otro usuario. Ese usuario puede ejecutar `initctl` con sudo; se crea un trabajo que lanza una shell y se obtiene root.

## Evidencia

- Plugin con webshell y ejecución.
- Auto-login con credenciales del segundo usuario.
- `sudo initctl` ejecutando un trabajo y shell de root.

## Lecciones aprendidas

- El panel de WordPress es ejecución de código por diseño.
- Los archivos de auto-login son credenciales en texto claro.
- `initctl` con sudo puede lanzar procesos privilegiados.

## Mitigación y detección

- Restringir la instalación de plugins y el acceso al panel.
- No guardar auto-login en el sistema de archivos.
- Limitar `initctl` y revisar reglas sudo.

## Referencias

- [0xdf — Spectra](https://0xdf.gitlab.io/2021/06/26/htb-spectra.html)
- [WordPress — Plugin API](https://developer.wordpress.org/plugins/)
- [Hack The Box — Spectra](https://app.hackthebox.com/machines/spectra)
