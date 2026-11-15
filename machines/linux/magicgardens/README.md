---
machine: MagicGardens
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, django, xss, ipv6, docker, capabilities, kernel-module]
---

# MagicGardens — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La tienda permite manipular el flujo de compra para activar una función premium; un XSS en el QR lleva al panel Django y a SSH. Un buffer overflow IPv6 en `harvest` da otro usuario, el registro Docker filtra el secreto de Django y `CAP_SYS_MODULE` permite cargar un módulo y escapar al host.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,443,5000 <IP>
ffuf -u http://magicgardens.htb -H "Host: FUZZ.magicgardens.htb" -w subdomains.txt
# XSS en el QR y panel Django
curl -s "http://magicgardens.htb/qr?data=<PAYLOAD>"
# Tras el pivote
capsh --print
ls -la /lib/modules/$(uname -r)
insmod /tmp/rootkit.ko
```

## Enumeración

- Tienda Django con carrito, cupones y generación de QR.
- Servicio `harvest` que procesa paquetes IPv6.
- Registro Docker interno y contenedores con capabilities amplias.

## Acceso inicial

Se altera el flujo de compra para obtener la función premium y se introduce un XSS en el contenido del QR. El bot administrativo visita el enlace y permite tomar el panel Django; desde allí se llega a una clave SSH.

## Escalada de privilegios

El binario `harvest` tiene un overflow en el manejo IPv6 que da acceso a otro usuario. La imagen del registro Docker contiene el secreto de Django y permite deserialización como root en el contenedor; `CAP_SYS_MODULE` habilita cargar un módulo y ser root en el host.

## Evidencia

- Compra premium manipulada y callback del XSS.
- Acceso al panel Django y SSH.
- `capsh --print` con `cap_sys_module` y módulo cargado.

## Lecciones aprendidas

- La lógica de negocio premium puede validarse solo en el cliente.
- Un parser de red en C sigue siendo una superficie de memoria.
- Una capability amplia en un contenedor puede equivaler a root en el host.

## Mitigación y detección

- Validar precios y privilegios en el servidor; sanear el QR.
- Compilar con mitigaciones y revisar parsers IPv6.
- Quitar `CAP_SYS_MODULE` y aplicar perfiles de seccomp/AppArmor.

## Referencias

- [0xdf — MagicGardens](https://0xdf.gitlab.io/2025/02/08/htb-magicgardens.html)
- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Hack The Box — MagicGardens](https://app.hackthebox.com/machines/magicgardens)
