---
topic: CUPS — inyección en Foomatic-RIP
tags: [linux, cups, ipp, foomatic, command-injection]
---

# CUPS — inyección en Foomatic-RIP

[🌐 English](cups-foomatic-rip-injection.en.md) | **Español**

## Concepto

CUPS crea impresoras con atributos como `cupsFilter` o el nombre del modelo. Al imprimir, Foomatic-RIP construye una línea de comandos con esos valores. Si no se validan, un atributo controlado por el atacante ejecuta comandos como el usuario del spooler, normalmente `lp`.

## Cuándo aplica

- La administración de CUPS en `631` es accesible.
- Se puede registrar una impresora o modificar sus atributos.
- Foomatic-RIP está instalado y procesa la impresora.

## Procedimiento

1. Enumerar impresoras y filtros disponibles.
2. Crear una impresora con un atributo malicioso.
3. Enviar una página de prueba o un trabajo.
4. Verificar la ejecución como `lp` y buscar el siguiente salto.

## Comandos

```bash
curl -s http://<HOST>:631/printers/
lpadmin -h <HOST>:631 -p evil -E -v ipp://<HOST>:631/printers/evil
lp -h <HOST>:631 -d evil /etc/hostname
# Atributo malicioso en la impresora
cupsFilter="application/pdf|/bin/sh -c id"
```

## Variantes

- Modificar una impresora existente con `lpadmin -P`.
- Usar el nombre del modelo o el PPD para inyectar.
- Combinar con un trabajo del spool para escalar.

## Limitaciones

- La administración puede exigir autenticación.
- El filtro debe estar habilitado para el MIME type.
- El proceso puede correr en un contenedor sin herramientas.

## Mitigación

- Restringir la administración de CUPS a localhost.
- Actualizar Foomatic y validar atributos.
- Ejecutar CUPS sin privilegios y limpiar el spool.

## Detección

- Nuevas impresoras o cambios de atributos.
- Trabajos que lanzan procesos desde Foomatic-RIP.
- Acceso remoto al puerto `631`.

## Referencias

- [0xdf — EvilCUPS](https://0xdf.gitlab.io/2024/10/02/htb-evilcups.html)
- [CUPS — Documentation](https://openprinting.github.io/cups/doc/)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
