---
topic: restic — --password-command como ejecución
tags: [linux, restic, backup, command-execution, privesc]
---

# restic — --password-command como ejecución

[🌐 English](restic-password-command.en.md) | **Español**

## Concepto

`restic` acepta `--password-command` para obtener la contraseña del repositorio ejecutando un comando. Si un usuario puede ejecutar restic como root, puede usar esa opción para ejecutar código con privilegios de root, incluso sin acceso al repositorio.

## Cuándo aplica

- `sudo -l` permite `restic` sin contraseña.
- La versión acepta `--password-command`.
- Se controla el argumento del comando.

## Procedimiento

1. Confirmar la regla de sudoers.
2. Usar `restic check --password-command` para copiar y marcar SUID.
3. Ejecutar la shell SUID.
4. Leer claves o datos del host.

## Comandos

```bash
sudo restic check --password-command 'cp /bin/bash /tmp/rootbash'
sudo restic check --password-command 'chmod 6777 /tmp/rootbash'
/tmp/rootbash -p
```

## Variantes

- `--password-command` en `backup`, `restore` o `snapshots`.
- Escribir una clave en `/root/.ssh`.
- Leer el backup para extraer secretos.

## Limitaciones

- La regla puede limitar subcomandos.
- Una versión antigua no soporta la opción.
- El repositorio debe existir para algunos comandos.

## Mitigación

- No permitir restic como root.
- Usar un wrapper con subcomandos y rutas fijas.
- Proteger el repositorio y las credenciales.

## Detección

- `--password-command` en la línea de comandos.
- Shells SUID creadas por restic.
- Accesos inusuales a repositorios de backup.

## Referencias

- [restic — password command](https://restic.readthedocs.io/en/stable/040_backup.html#passing-the-password)
- [0xdf — WhiteRabbit](https://0xdf.gitlab.io/2025/12/13/htb-whiterabbit.html)
- [HackTricks — restic](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
