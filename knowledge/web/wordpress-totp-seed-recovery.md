---
topic: Recuperación del secreto TOTP en WordPress
tags: [web, wordpress, totp, mfa, database]
---

# Recuperación del secreto TOTP en WordPress

[🌐 English](wordpress-totp-seed-recovery.en.md) | **Español**

## Concepto

Los plugins de doble factor guardan el secreto TOTP en la base de datos de WordPress, a veces en texto plano o con una clave estática. Con acceso SQL o con un volcado de la base se puede generar el código actual y completar el segundo factor.

## Cuándo aplica

- Se tiene acceso de lectura a `wp_users` y a las tablas del plugin 2FA.
- El secreto no está cifrado con una clave derivada del usuario.
- El login pide un código TOTP después de la contraseña.

## Procedimiento

1. Enumerar tablas y localizar la del plugin 2FA.
2. Extraer el secreto del usuario objetivo.
3. Generar el código con `oathtool` o `pyotp`.
4. Usar el código en la ventana de verificación.

```sql
SELECT user_id, meta_key, meta_value FROM wp_usermeta WHERE meta_key LIKE '%totp%';
```

```bash
oathtool --totp -b '<SEED>'
python3 -c "import pyotp; print(pyotp.TOTP('<SEED>').now())"
```

## Variantes

- Descifrar el secreto con una clave encontrada en `wp-config.php`.
- Reutilizar el secreto para otro servicio.
- Deshabilitar el plugin desde la base si se puede escribir.

## Limitaciones

- El secreto debe estar accesible.
- El código caduca en pocos segundos.
- Algunos plugins cifran con una clave por usuario.

## Mitigación y detección

- Cifrar los secretos TOTP con una clave externa a la base.
- Restringir el acceso SQL y rotar secretos tras un incidente.
- Preferir passkeys o hardware tokens.

## Referencias

- <https://datatracker.ietf.org/doc/html/rfc6238>
- <https://developer.wordpress.org/apis/security/>
- <https://attack.mitre.org/techniques/T1552/>
