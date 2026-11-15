---
machine: WhiteRabbit
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, uptime-kuma, wikijs, n8n, sqli, restic, container, password-generator, privesc]
---

# WhiteRabbit — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Uptime Kuma permite un bypass de login y una shell en su contenedor como `bob`. WikiJS documenta un flujo de n8n con firma HMAC y una SQLi; con un proxy que firma las peticiones se dumpea la base y se obtienen comandos de restic. Un backup contiene claves SSH y `restic --password-command` da root en el contenedor y acceso a `morpheus` en el host. Un generador de contraseñas basado en timestamp permite calcular la de `neo`, que puede ejecutar cualquier comando como root.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,2222 <IP>
```

- `22` SSH del host, `2222` SSH del contenedor y `80` Caddy.
- `ffuf` descubre `whiterabbit.htb`, `uptime.whiterabbit.htb` y un WikiJS con subdominio aleatorio.
- La web principal menciona Uptime Kuma, n8n, GoPhish y Stalwart.

## Enumeración

- Uptime Kuma usa Socket.IO y tiene un bypass de login.
- Se crea un monitor/status page y se enumeran los hosts internos.
- El WikiJS documenta el flujo `GoPhish -> n8n`, la firma `x-gophish-signature` y la consulta SQL.
- El export del flujo revela el secreto HMAC y la SQLi en el email.

## Foothold

Se levanta un proxy `mitmproxy` que recalcula la firma de cada petición, y `sqlmap` dumpea la base a través de él. La base contiene comandos de restic, la contraseña de `.restic_passwd` y la ejecución de `neo-password-generator`.

```bash
mitmproxy -s signature_proxy.py -p 8888 --mode regular
sqlmap -r request.req --proxy http://127.0.0.1:8888
```

## Movimiento lateral

El repo restic contiene `bob.7z` con claves SSH; se crackea con `7z2john` y `john`. En el contenedor, `bob` puede ejecutar `restic` como root; `--password-command` ejecuta comandos y permite copiar `/bin/bash` y darle SUID. La clave de `morpheus` en `/root` permite entrar al host.

```bash
sudo restic check --password-command 'cp /bin/bash /tmp/rootbash'
sudo restic check --password-command 'chmod 6777 /tmp/rootbash'
ssh -i morpheus morpheus@whiterabbit.htb
```

## Escalada de privilegios

`morpheus` encuentra `neo-password-generator`, que siembra `srand()` con el timestamp en milisegundos. Los logs de la base revelan la hora en que se ejecutó; se generan todas las contraseñas de ese segundo y `hydra` encuentra la de `neo`. `neo` puede ejecutar cualquier comando como root.

```bash
python3 gen_passwords.py '2024-08-30 14:40:42'
hydra -l neo -P neo_passwords ssh://whiterabbit.htb
sudo -i
```

## Evidencia

- Uptime Kuma y shell como `bob`.
- WikiJS, firma HMAC y SQLi en n8n.
- Base con comandos restic.
- `restic --password-command` y claves SSH.
- Generador de contraseñas por timestamp y `neo`.

## Lecciones aprendidas

- Un panel de monitorización puede filtrar la topología interna.
- Firmar peticiones no impide la SQLi si el secreto se filtra.
- `restic --password-command` es ejecución si se controla el argumento.
- Un PRNG sembrado con tiempo es predecible.

## Mitigación y detección

- Actualizar Uptime Kuma y exigir MFA.
- Parametrizar consultas y proteger el secreto HMAC.
- No permitir `--password-command` a usuarios no confiables.
- Usar CSPRNG y no derivar contraseñas del reloj.

## Referencias

- [0xdf — WhiteRabbit](https://0xdf.gitlab.io/2025/12/13/htb-whiterabbit.html)
- [IppSec — WhiteRabbit](https://www.youtube.com/watch?v=IVwZAINSCwo)
- [Hack The Box — WhiteRabbit](https://app.hackthebox.com/machines/whiterabbit)
