---
topic: Hash length extension — SHA-256(secreto || datos)
tags: [crypto, hash, sha256, mac, length-extension]
---

# Hash length extension — SHA-256(secreto || datos)

[🌐 English](hash-length-extension.en.md) | **Español**

## Concepto

Un MAC construido como `SHA-256(secreto || datos)` es vulnerable a extensión de hash. Conociendo la firma y la longitud del secreto, se puede calcular una firma válida para `datos || relleno || extra` sin conocer el secreto. No es un ataque contra HMAC, que está diseñado para evitarlo.

## Cuándo aplica

- La aplicación valida un checksum tipo `hash(secreto + email)` o `sha256(secreto + parámetro)`.
- Se conoce un mensaje y su firma válidos, y la longitud del secreto es acotada.
- El parámetro firmado se usa después en una operación sensible, como una inyección de comandos.

## Procedimiento

1. Identificar el algoritmo y confirmar que es `secreto || datos`, no HMAC.
2. Probar longitudes de secreto y generar candidatos con `hash_extender`.
3. Enviar el mensaje con bytes de relleno y la nueva firma.
4. Detectar la longitud correcta por la respuesta y añadir el payload final.

## Comandos

```bash
hash_extender --data "user@example.com" -s "<SIGNATURE>" --append "@$(id)" --secret-min=1 --secret-max=80 --out-data-format=html > candidates
# Enviar cada candidate conservando los bytes y la nueva firma
```

## Variantes

- Aplicar el mismo principio a SHA-1 y MD5.
- Usar la longitud del secreto filtrada por un error o por el tamaño del identificador.
- Combinar con una inyección de comandos en el campo que se concatena.

## Limitaciones

- No funciona contra HMAC ni contra hashes con sal aleatoria por mensaje.
- La longitud del secreto debe ser conocida o brute-forceable.
- El transporte debe preservar bytes nulos y no truncar el mensaje.

## Mitigación

- Usar HMAC-SHA-256 con comparación en tiempo constante.
- No construir MAC concatenando un secreto con entrada del usuario.
- Limitar y normalizar el campo firmado antes de usarlo.

## Detección

- Firmas válidas para mensajes con relleno o bytes no imprimibles.
- Parámetros que crecen después de un separador y conservan un checksum antiguo.
- Errores de validación con longitudes de secreto variables.

## Referencias

- [0xdf — Extension](https://0xdf.gitlab.io/2023/03/18/htb-extension.html)
- [Length extension attack](https://en.wikipedia.org/wiki/Length_extension_attack)
- [CWE-328 — Use of Weak Hash](https://cwe.mitre.org/data/definitions/328.html)
