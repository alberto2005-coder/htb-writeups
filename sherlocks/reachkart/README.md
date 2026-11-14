---
sherlock: ReachKart
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, access-log, path-traversal, jwt, websocket, blockchain, hardhat]
---

# ReachKart — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

ReachKart es una tienda con un entorno de desarrollo que replica producción. Los vendedores denuncian que sus wallets han perdido Ether. Se entrega el log de acceso y una captura de red del servidor de desarrollo para reconstruir la intrusión y el robo.

## Evidencias

- `access.log` del servidor web.
- `network-traffic.pcap` con HTTP, WebSocket y JSON-RPC de Hardhat.
- Nota de tiempos: la captura tiene un desfase de +11 horas; el log está en UTC.

```bash
sha256sum access.log network-traffic.pcap
head -n 5 access.log
capinfos network-traffic.pcap
```

## Investigación

### 1. Inventario y triaje

Se comparan las horas del log y de la captura antes de responder cualquier pregunta temporal. El log muestra peticiones a `/user/getOrderBill` con cadenas `../`, lo que apunta a path traversal.

```bash
grep -F 'template=../' access.log | awk '{print $7}' | sort | uniq -c | sort -rn
```

La primera explotación con respuesta `200` lee `/etc/passwd`; los intentos anteriores fallan.

### 2. Descubrimiento y credenciales

La captura conserva la respuesta con `package.json`, que revela Express y la versión de Hardhat. También se lee el código del servidor, incluido `rk-logging.js`, donde está la clave de firma JWT.

```bash
tshark -r network-traffic.pcap -q -z follow,tcp,ascii,53 | grep -i secret
```

Con la clave `<JWT_SECRET>` se firma un token con `account_type: admin`. El token se presenta en `GET /admin`; el servidor lo acepta.

### 3. Ejecución y exfiltración

El panel admin incluye una terminal WebSocket en el puerto 8888. El atacante ejecuta comandos, levanta un `python3 -m http.server 6969` y sirve `reachkart.db`, que descarga con `wget`.

```bash
tshark -r network-traffic.pcap -Y websocket -T fields -e tcp.dstport -e websocket.payload.text
tshark -r network-traffic.pcap -Y 'tcp.port==6969 && http.request' -T fields -e frame.time -e http.request.uri
```

La base SQLite contiene vendedores y wallets. Se cuentan los usuarios con rol `seller`.

### 4. Impacto en la blockchain

Hardhat escucha en 8545 sin autenticación. La captura muestra llamadas `eth_sendRawTransaction` desde las wallets de los vendedores hacia una única dirección. Se suman los `value` y se excluye la transacción de gas.

```bash
tshark -r network-traffic.pcap -Y 'tcp.port==8545 && json' -T json > rpc.json
grep -n 'eth_sendRawTransaction' rpc.json | head
```

## Conclusiones

- El acceso inicial fue un path traversal en `/user/getOrderBill`.
- La fuga de código reveló la clave JWT y permitió forjar un token admin.
- La terminal WebSocket dio ejecución y permitió servir la base de datos.
- El nodo Hardhat de desarrollo custodió wallets reales y facilitó el vaciado.
- El desfase temporal de la captura es un punto de error crítico.

## Lecciones

- Un entorno de desarrollo con datos reales es producción.
- Los secretos no deben estar en el código ni en archivos accesibles por traversal.
- Un panel admin con terminal y un nodo blockchain sin autenticación multiplican el impacto.
- Normalizar zonas horarias antes de correlacionar fuentes.

## Referencias

- <https://www.hackthebox.com/sherlocks/ReachKart>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://attack.mitre.org/techniques/T1606/001/>
- <https://hardhat.org/hardhat-network/docs/overview>
