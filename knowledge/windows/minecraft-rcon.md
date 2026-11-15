---
topic: Minecraft — RCON y secretos en plugins
tags: [windows, minecraft, rcon, log4shell, java]
---

# Minecraft — RCON y secretos en plugins

[🌐 English](minecraft-rcon.en.md) | **Español**

## Concepto

RCON es un protocolo administrativo de Minecraft que ejecuta comandos en el servidor. Si la contraseña está en un plugin o en `server.properties` y se reutiliza, un atacante con acceso al servidor o al JAR puede ejecutar comandos como el usuario que corre Minecraft, o pivotar a otro contexto.

## Cuándo aplica

- El puerto `25575` está abierto o accesible desde otro contenedor.
- Se descarga un plugin/JAR con configuración o credenciales.
- Log4Shell u otra RCE ya dio acceso al servidor.

## Procedimiento

1. Enumerar Minecraft y el panel de administración.
2. Descargar y descompilar el plugin para buscar `rcon.password`.
3. Conectar a RCON y ejecutar un comando de prueba.
4. Usar `RunasCs` o el contexto del servicio para escalar.

## Comandos

```bash
nmap -Pn -sCV -p25565,25575 <IP>
mcstatus <IP>:25565
unzip plugin.jar -d plugin && jadx plugin | grep -ri "rcon\|password"
mcrcon -H <IP> -P 25575 -p "<PASS>" "whoami"
mcrcon -H <IP> -P 25575 -p "<PASS>" "powershell -c whoami"
```

## Variantes

- Usar RCON para ejecutar un script de PowerShell o descargar un binario.
- Reutilizar la contraseña contra el panel web de Crafty.
- Combinar con Log4Shell para obtener la primera shell.

## Limitaciones

- RCON puede estar limitado a loopback.
- La contraseña puede ser distinta de la del panel.
- El servidor puede ejecutarse con un usuario sin privilegios.

## Mitigación

- Deshabilitar RCON o bindearlo a loopback.
- Rotar contraseñas y no incluirlas en plugins.
- Ejecutar Minecraft con una cuenta de servicio de bajo privilegio.

## Detección

- Conexiones a `25575` desde hosts que no son el panel.
- Comandos RCON que lanzan procesos o descargan archivos.
- Plugins con credenciales en texto plano.

## Referencias

- [Minecraft — RCON](https://minecraft.wiki/w/Server.properties#enable-rcon)
- [0xdf — Crafty](https://0xdf.gitlab.io/2024/06/15/htb-crafty.html)
- [CWE-798 — Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)
