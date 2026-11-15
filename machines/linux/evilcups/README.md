---
machine: EvilCUPS
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, cups, ipp, foomatic, printer, command-injection]
---

# EvilCUPS — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

CUPS acepta la creación de una impresora controlada por el atacante. Al imprimir una página de prueba, el filtro Foomatic-RIP interpreta un atributo malicioso y ejecuta comandos como `lp`; un trabajo antiguo del spool contiene la información para llegar a root.

## Reconocimiento

```bash
nmap -Pn -sCV -p631,80 <IP>
curl -s http://<IP>:631/printers/
# Registrar una impresora controlada
lpadmin -h <IP>:631 -p evil -E -v ipp://<IP>:631/printers/evil
lp -h <IP>:631 -d evil /etc/hostname
# Spool
ls -la /var/spool/cups/
cups-filters /usr/lib/cups/filter/foomatic-rip
```

## Enumeración

- CUPS en `631` con administración accesible.
- Filtros Foomatic-RIP y plantillas de impresora.
- Spool con trabajos de impresión antiguos.

## Acceso inicial

Se registra una impresora que apunta a un servidor controlado y se envía una página de prueba. El atributo `cupsFilter` o el nombre del modelo llega sin sanear a Foomatic-RIP, que ejecuta el comando y devuelve una shell como `lp`.

## Escalada de privilegios

El spool conserva un trabajo antiguo con un PDF reconstruible. El documento contiene credenciales o una ruta de root; se usa para acceder como root o para ejecutar una tarea privilegiada.

## Evidencia

- Impresora creada desde CUPS.
- Página de prueba con callback y shell como `lp`.
- Trabajo del spool reconstruido y acceso a root.

## Lecciones aprendidas

- Un servidor de impresión es una superficie de ejecución.
- Los filtros heredados interpretan atributos como comandos.
- El spool conserva documentos que se creían eliminados.

## Mitigación y detección

- Restringir la administración de CUPS y la creación de impresoras.
- Actualizar Foomatic y validar atributos.
- Limpiar el spool y ejecutar CUPS con usuarios sin privilegios.

## Referencias

- [0xdf — EvilCUPS](https://0xdf.gitlab.io/2024/10/02/htb-evilcups.html)
- [CUPS — Documentation](https://openprinting.github.io/cups/doc/)
- [Hack The Box — EvilCUPS](https://app.hackthebox.com/machines/evilcups)
