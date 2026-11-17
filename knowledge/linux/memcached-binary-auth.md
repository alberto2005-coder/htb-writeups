---
topic: Memcached — autenticación SASL por protocolo binario
tags: [linux, memcached, sasl, binary-protocol, dyplesher]
---

# Memcached — autenticación SASL por protocolo binario

[🌐 English](memcached-binary-auth.en.md) | **Español**

## Concepto

Memcached no tiene autenticación en su configuración clásica. Cuando se arranca con `-S` y se compila con SASL, exige autenticación, pero solo en el protocolo binario: las herramientas ASCII (`memcached-tool`, `nc`) dejan de funcionar. Las credenciales suelen aparecer en configuraciones de aplicaciones, unidades systemd o variables de entorno.

## Cuándo aplica

- Memcached accesible en `11211`.
- Banner o `stats` que responde solo al protocolo binario.
- Procesos o ficheros de configuración con usuario y contraseña SASL.
- En Dyplesher, las credenciales estaban en la configuración de la aplicación y permitían volcar claves.

## Procedimiento

1. Confirmar el puerto y el modo SASL.
2. Obtener credenciales de la aplicación, systemd o variables de entorno.
3. Conectar con un cliente que soporte binario + SASL.
4. Listar slabs y claves, y volcar los valores.
5. Reutilizar los secretos encontrados.

## Comandos

```bash
nmap -sV -p11211 <IP>
printf 'version\r\n' | nc -nv <IP> 11211
```

Con `pymemcache`:

```python
from pymemcache.client.base import Client

c = Client(('<IP>', 11211), binary=True,
           sasl_username='<USER>', sasl_password='<PASSWORD>')
print(c.stats())
for key in c.stats('items'):
    print(key)
```

Con `memcached-tool` no se puede autenticar; para volcar claves:

```bash
memcdump --servers=<IP> --binary --username=<USER> --password=<PASSWORD>
memccat --servers=<IP> --binary --username=<USER> --password=<PASSWORD> <KEY>
```

## Variantes

- `stats items` y `stats cachedump <slab> <limit>` para enumerar claves cuando el protocolo ASCII está permitido.
- `lru_crawler metadump all` en versiones recientes.
- Credenciales SASL en `/etc/memcached.conf`, `systemd` o el `.env` de la app.
- Reutilizar la contraseña contra SSH, base de datos o el panel de la aplicación.

## Limitaciones

- Sin `-S`, SASL no se usa y el binario no autentica.
- Algunos clientes solo hablan ASCII.
- El puerto puede estar en loopback o tras un firewall.
- Las claves pueden haber expirado.

## Mitigación

- No exponer memcached a Internet; bind a loopback o red interna.
- Habilitar SASL con credenciales fuertes y TLS cuando sea posible.
- Rotar credenciales y no reutilizarlas.
- Restringir `11211` por firewall y monitorizar accesos.

## Detección

- Conexiones al puerto `11211` desde hosts no esperados.
- Comandos `stats items`, `get` o `lru_crawler` en el tráfico.
- Procesos que leen configuraciones de memcached.
- Uso de credenciales SASL desde IPs nuevas.

## Referencias

- [Memcached — SASL](https://github.com/memcached/memcached/wiki/SASLHowto)
- [Memcached — Protocolo binario](https://github.com/memcached/memcached/wiki/BinaryProtocolRevamped)
- [0xdf — Dyplesher](https://0xdf.gitlab.io/2020/10/03/htb-dyplesher.html)
- [Ficha Dyplesher](../../machines/linux/dyplesher/README.md)
