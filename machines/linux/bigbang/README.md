---
machine: BigBang
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, wordpress, buddyforms, php-filter-chain, cve-2024-2961]
---

# BigBang — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

WordPress con BuddyForms permite lectura de archivos (CVE-2023-26326); la cadena de filtros PHP `wrapwrap` convierte esa lectura en RCE mediante CVE-2024-2961. Los hashes de WordPress y Grafana permiten pivotar y la app Android lleva a root por inyección de comandos.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
wpscan --url http://bigbang.htb --enumerate vp,u
curl -s "http://bigbang.htb/wp-admin/admin-ajax.php?action=buddyforms_upload"
php_filter_chain_generator.py --chain '<CADENA>'
apktool d bigbang.apk
# Tras el acceso
sudo -l; id
```

## Enumeración

- WordPress y un formulario BuddyForms expuesto.
- Grafana en un vhost interno con credenciales reutilizadas.
- Un APK de la aplicación móvil disponible desde la web.

## Acceso inicial

BuddyForms permite recorrer rutas y leer archivos. Se encadena con el desbordamiento de `iconv` de glibc para construir una cadena de filtros PHP que escribe un archivo y ejecuta código como `www-data`.

## Escalada de privilegios

`wp-config.php` entrega credenciales de la base; los hashes se crackean y reutilizan en Grafana. El APK descompilado revela un endpoint con inyección de comandos que corre como root.

## Evidencia

- Lectura de `wp-config.php` a través de BuddyForms.
- Cadena `wrapwrap` y ejecución de `id`.
- Endpoint del APK vulnerable y shell de root.

## Lecciones aprendidas

- La lectura de archivos se convierte en RCE al encadenar conversiones de charset.
- Los secretos de WordPress suelen repetirse en paneles internos.
- Una app móvil puede exponer una API más débil que la web.

## Mitigación y detección

- Actualizar BuddyForms, glibc y PHP.
- Rotar credenciales y no reutilizarlas entre WordPress y Grafana.
- Validar y autenticar los endpoints usados por la app móvil.

## Referencias

- [0xdf — BigBang](https://0xdf.gitlab.io/2025/05/03/htb-bigbang.html)
- [NVD — CVE-2024-2961](https://nvd.nist.gov/vuln/detail/CVE-2024-2961)
- [Hack The Box — BigBang](https://app.hackthebox.com/machines/bigbang)
