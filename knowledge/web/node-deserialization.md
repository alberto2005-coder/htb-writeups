---
topic: Deserialización insegura en Node.js
tags: [web, nodejs, deserialization, node-serialize, rce, cookies]
---

# Deserialización insegura en Node.js

[🌐 English](node-deserialization.en.md) | **Español**

## Concepto

`node-serialize` permite serializar objetos JavaScript, incluidas funciones, y reconstruirlos con `unserialize`. Si el dato viene de una cookie o de un parámetro controlado por el usuario, una función serializada se ejecuta al deserializarla.

## Cuándo aplica

- Cookies o parámetros con JSON que empieza por `{"` y contiene `_$$ND_FUNC$$_`.
- Aplicaciones Node.js que usan `node-serialize`, `serialize-javascript` mal configurado o `eval`.
- Sesiones que guardan objetos completos en el cliente.

## Procedimiento

1. Decodificar la cookie (base64 o URL encoding).
2. Identificar la estructura y la clave serializada.
3. Comprobar si el valor se pasa a `unserialize`.
4. Construir un objeto con una función inmediatamente invocada.
5. Enviar la cookie codificada y observar la ejecución.

```javascript
const payload = {
  rce: "_$$ND_FUNC$$_function(){return require('child_process').execSync('id').toString()}()"
};
Buffer.from(JSON.stringify(payload)).toString("base64");
```

## Variantes

- `_$$ND_FUNC$$_` con función autoejecutada `()`.
- `eval` sobre JSON en lugar de `JSON.parse`.
- Prototype pollution previa para alterar el objeto deserializado.
- Cadenas de gadgets en librerías que aceptan objetos.

## Limitaciones

- La aplicación debe llamar a `unserialize` con entrada del usuario.
- Las funciones no sobreviven a `JSON.parse` puro.
- WAF y validación de cookies pueden bloquear el payload.
- El contexto de ejecución limita los comandos disponibles.

## Mitigación y detección

- No deserializar objetos ejecutables; usar `JSON.parse` y validar esquema.
- Firmar y cifrar cookies; no confiar en su contenido.
- Evitar `eval` y `Function` sobre datos externos.
- Alertar de `_$$ND_FUNC$$_`, `child_process` y cookies anómalamente largas.

## Referencias

- <https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data>
- <https://cwe.mitre.org/data/definitions/502.html>
- <https://attack.mitre.org/techniques/T1059/007/>
- <https://github.com/luin/serialize>
