---
machine: Scavenger
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, whois, sqli, exim, rootkit, privesc]
---

# Scavenger — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El servidor Whois en el puerto 43 concatena el dominio en SQL y filtra los dominios alojados. Uno de ellos conduce a un PrestaShop con una webshell, y el FTP entrega credenciales de otro cliente. En el host, el módulo `root.ko` instalado en el kernel da root al escribir una contraseña en `/dev/ttyR0`; como alternativa, Exim 4.89 es vulnerable a CVE-2019-10149 y permite ejecutar comandos como root desde SMTP.

## Reconocimiento

```bash
nmap -Pn -sCV -p21,22,25,43,53,80 <IP>
```

- `21` FTP, `22` SSH, `25` Exim, `43` Whois, `53` DNS y `80` HTTP.
- El Whois responde con un banner de SuperSecHosting.
- La resolución de los dominios alojados apunta a vhosts internos.

## Enumeración

El Whois es vulnerable a inyección SQL en el dominio. Se enumeran bases, tablas y clientes con `UNION SELECT`; uno de los dominios es `rentahacker.htb`. Un transfer de zona DNS revela los vhosts. En `sec03.rentahacker.htb` hay un PrestaShop con un parámetro vulnerable que permite subir una webshell.

## Foothold

La webshell se invoca con `?hidden=id` y ejecuta comandos como `ib01c03`. El FTP del mismo segmento contiene credenciales de `ib01c01`, que permiten moverse a otro cliente del hosting.

```text
http://sec03.rentahacker.htb/shell.php?hidden=id
```

## Movimiento lateral

Con las credenciales de FTP se accede a los archivos de otro cliente y se encuentra el módulo `root.ko`, además de la contraseña de `root` para el módulo.

## Escalada de privilegios

`root.ko` crea `/dev/ttyR0`. Al escribir la contraseña del módulo, `root_write` compara el buffer con la cadena mágica y, si coincide, cambia todas las credenciales a UID/GID 0. La cadena está construida con `snprintf` a partir de dos partes, así que hay que extraerla del binario o probar la variante correcta.

```bash
echo "<cadena>" > /dev/ttyR0
id
```

La vía alternativa es CVE-2019-10149 en Exim 4.89: una dirección `RCPT TO` con expansión `${run{...}}` ejecuta comandos como root. Se usa cuando el servicio SMTP está expuesto y el módulo no está disponible.

## Evidencia

- Whois con `UNION SELECT` y listado de clientes.
- Webshell en PrestaShop.
- `root.ko` y `/dev/ttyR0`.
- `id` con UID 0 tras el pushback.

## Lecciones aprendidas

- Los servicios antiguos (Whois, FTP) siguen siendo superficie de ataque.
- Un SQLi en un servicio no web puede enumerar todo el hosting.
- Los módulos de kernel de terceros son root si se puede escribir en su dispositivo.
- Exim mal configurado permite RCE directa desde SMTP.

## Mitigación y detección

- Parametrizar las consultas del Whois y limitar la información devuelta.
- Actualizar Exim a una versión corregida y restringir `RCPT TO`.
- No cargar módulos de kernel sin firma; auditar `/dev/ttyR0`.
- Monitorizar comandos hijos de Exim y escrituras en dispositivos nuevos.

## Referencias

- [0xdf — Scavenger](https://0xdf.gitlab.io/2020/02/29/htb-scavenger.html)
- [IppSec — Scavenger](https://www.youtube.com/watch?v=rlUTZiqTKgc)
- [Hack The Box — Scavenger](https://app.hackthebox.com/machines/scavenger)
