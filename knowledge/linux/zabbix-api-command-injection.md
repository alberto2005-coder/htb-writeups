---
topic: Zabbix — API, scripts y ejecución en agentes
tags: [linux, zabbix, api, command-execution, suid, privesc]
---

# Zabbix — API, scripts y ejecución en agentes

[🇬🇧 English](zabbix-api-command-injection.en.md) | **Español**

## Concepto

La API de Zabbix autentica usuarios y permite crear scripts que se ejecutan en el servidor o en un agente. Una cuenta con credenciales débiles puede crear un script con una reverse shell y ejecutarlo en el host del agente; los permisos del agente determinan el usuario resultante.

## Cuándo aplica

- La interfaz o la API de Zabbix es accesible.
- Se ha adivinado o reutilizado una contraseña.
- El agente acepta scripts remotos (`EnableRemoteCommands=1`).

## Procedimiento

1. Autenticarse con `user.login` y obtener el token.
2. Listar hosts y scripts con `host.get` y `script.get`.
3. Crear un script y ejecutarlo con `execute_on: 0`.
4. Enumerar SUID y scripts escribibles para root.

```bash
curl -s -X POST 'http://<IP>/zabbix/api_jsonrpc.php' -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"user.login","params":{"user":"<USER>","password":"<PASSWORD>"},"id":1}'
```

## Variantes

- `script.create` con un comando y `execute_on: 0`.
- `history.get` para leer datos internos.
- Un SUID que llama a `system` sin ruta absoluta.
- Un script de backup escribible ejecutado por cron.

## Limitaciones

- La cuenta debe tener permisos de API y de script.
- El agente puede tener los comandos remotos deshabilitados.
- La versión parcheada restringe los scripts.

## Mitigación

- Credenciales fuertes y MFA en Zabbix.
- Deshabilitar comandos remotos y limitar scripts.
- Rutas absolutas y permisos mínimos en SUID y scripts.

## Detección

- `script.create` y ejecuciones desde la API.
- Procesos hijos del agente.
- SUID nuevos o scripts de backup modificados.

## Referencias

- [Zabbix — API](https://www.zabbix.com/documentation/current/en/manual/api)
- [0xdf — Zipper](https://0xdf.gitlab.io/2019/02/23/htb-zipper.html)
- [MITRE ATT&CK — T1059](https://attack.mitre.org/techniques/T1059/)
