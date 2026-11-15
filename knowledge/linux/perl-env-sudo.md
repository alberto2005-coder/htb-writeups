---
topic: Perl — variables de entorno con sudo SETENV
tags: [linux, perl, sudo, setenv, perl5opt, privesc]
---

# Perl — variables de entorno con sudo SETENV

[🌐 English](perl-env-sudo.en.md) | **Español**

## Concepto

Cuando sudoers incluye `SETENV`, el usuario puede conservar variables de entorno al ejecutar un binario. Si ese binario es un script Perl o llama a uno, `PERL5OPT` y `PERL5DB` permiten activar el depurador y ejecutar código antes del programa.

## Cuándo aplica

- La regla sudo muestra `SETENV`.
- El script ejecutado usa Perl o llama a `xml_pp`/otro Perl.
- Las variables `PERL5OPT`/`PERL5DB` no se limpian.

## Procedimiento

1. Confirmar la regla y el intérprete.
2. Probar `PERL5OPT=-d` con un comando inocuo.
3. Usar `PERL5DB` para copiar bash y darle SUID.
4. Ejecutar la shell resultante.

## Comandos

```bash
sudo PERL5OPT=-d PERL5DB='system("cp /bin/bash /tmp/root; chmod 6777 /tmp/root")' /opt/monitor.sh
/tmp/root -p
```

## Variantes

- `PERL5LIB` para cargar un módulo malicioso.
- `PERL5OPT=-M...` para importar código.
- Scripts que llaman a Perl sin `env -i`.

## Limitaciones

- Sin `SETENV`, sudo limpia el entorno.
- El script puede hacer `unset PERL5OPT` antes de Perl.
- Una jaula o SELinux puede bloquear la escritura.

## Mitigación

- No usar `SETENV` en reglas sudo.
- Limpiar `PERL5OPT`, `PERL5DB`, `PERL5LIB` y `LD_PRELOAD`.
- Ejecutar scripts con `env -i` y rutas absolutas.

## Detección

- `PERL5OPT` o `PERL5DB` en la línea de comandos.
- Shells SUID creadas por un script root.
- Ejecuciones de Perl desde scripts de monitorización.

## Referencias

- [0xdf — Clicker](https://0xdf.gitlab.io/2024/01/27/htb-clicker.html)
- [Perl — PERL5OPT](https://perldoc.perl.org/perlrun#PERL5OPT)
- [GTFOBins — Perl](https://gtfobins.github.io/gtfobins/perl/)
