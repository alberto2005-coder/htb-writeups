---
topic: Forense de tráfico OpenStack
tags: [cloud, openstack, pcap, keystone, swift, forensics]
---

# Forense de tráfico OpenStack

[🇬🇧 English](openstack-forensics.en.md) | **Español**

## Concepto

OpenStack separa identidad (Keystone), cómputo (Nova), red (Neutron) y objetos (Swift). Un PCAP permite reconstruir autenticaciones, tokens y operaciones sobre contenedores si el tráfico no está cifrado o si se dispone de claves.

## Cuándo aplica

- Incidente en una nube privada.
- Captura entre un cliente y los endpoints de OpenStack.
- Sospecha de abuso de tokens o descarga de objetos.

## Procedimiento

1. Identificar hosts y versiones de API.
2. Aislar `/v3/auth/tokens` y los códigos 201/401.
3. Extraer tokens y asociarlos a usuarios/proyectos.
4. Listar operaciones Swift (`/v1/AUTH_*`).
5. Correlacionar con logs de Nova/Neutron.

```bash
tshark -r capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

## Variantes

- Tráfico TLS con claves de sesión.
- APIs internas sin autenticación.
- Abuso de tokens de servicio.

## Limitaciones

- TLS sin claves impide leer rutas y tokens.
- Los logs pueden estar en otro nodo.
- Los tokens expiran y se rotan.

## Mitigación

- TLS en todos los endpoints.
- Tokens de corta duración y scope mínimo.
- Auditar accesos a Swift y rotar credenciales.

## Detección

- Descargas masivas de objetos.
- Tokens usados desde IPs nuevas.
- 401 repetidos seguidos de 201.

## Referencias

- <https://docs.openstack.org/keystone/latest/>
- <https://docs.openstack.org/swift/latest/>
- <https://attack.mitre.org/techniques/T1078/>
