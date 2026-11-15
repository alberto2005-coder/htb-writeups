---
topic: PHP — type juggling y hashes mágicos
tags: [web, php, type-juggling, magic-hash, authentication]
---

# PHP — type juggling y hashes mágicos

[🌐 English](php-type-juggling-auth.en.md) | **Español**

## Concepto

PHP convierte cadenas numéricas al comparar con `==`. Un hash que empieza por `0e` seguido de dígitos se interpreta como cero, igual que otro hash con la misma forma. Si la aplicación compara hashes con `==`, una contraseña puede coincidir con el hash almacenado sin conocerla.

## Cuándo aplica

- El login compara hashes con `==` o `!=`.
- La aplicación usa MD5/SHA1 y no `password_verify`.
- Se puede elegir la contraseña enviada.

## Procedimiento

1. Identificar la función de comparación y el algoritmo.
2. Probar una contraseña con hash mágico conocido, como `240610708`.
3. Comprobar si el login acepta la sesión.
4. Usar el acceso para llegar a la subida o al panel.

## Comandos

```bash
# MD5(240610708) = 0e462097431906509019562988736854
curl -d "username=admin&password=240610708" http://<HOST>/login.php
# Otros valores clásicos
# QNKCDZO, aabg7XSs, aabC9RqS
php -r 'var_dump(md5("240610708"));'
```

## Variantes

- Usar hashes SHA1 con el mismo patrón `0e`.
- Aprovechar `strcmp` con arrays para evitar la comparación.
- Combinar con una SQLi para obtener el hash almacenado.

## Limitaciones

- Solo funciona con comparación laxa, no con `===`.
- La contraseña debe pasar validaciones de longitud o formato.
- Las versiones modernas de PHP y los frameworks usan `password_verify`.

## Mitigación

- Usar `password_hash` y `password_verify`.
- Comparar con `===` y validar tipos.
- Aplicar bloqueo y MFA en el login.

## Detección

- Contraseñas con hashes `0e...` en intentos de login.
- Bypasses de autenticación seguidos de subidas.
- Uso de `==` en revisiones de código.

## Referencias

- [PHP — Type juggling](https://www.php.net/manual/en/language.types.type-juggling.php)
- [0xdf — Falafel](https://0xdf.gitlab.io/2018/06/23/htb-falafel.html)
- [OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
