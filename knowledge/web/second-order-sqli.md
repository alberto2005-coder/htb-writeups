---
topic: SQLi de segundo orden — inyección almacenada y ejecutada después
tags: [web, sqli, second-order, union, earlyaccess]
---

# SQLi de segundo orden — inyección almacenada y ejecutada después

[🌐 English](second-order-sqli.en.md) | **Español**

## Concepto

En una SQLi de segundo orden el payload se guarda en la base de datos en un primer paso y se usa sin parametrizar en una consulta posterior. La petición que lo inserta no muestra error ni cambia el resultado, así que los escáneres que solo miran la respuesta inmediata no la detectan. En EarlyAccess, el nombre de usuario se guardaba al registrarse y se interpolaba después al generar una clave.

## Cuándo aplica

- Un campo se almacena y luego se reutiliza en otra consulta (perfiles, nombres, referencias).
- La primera operación valida el formato pero no escapa caracteres SQL.
- Hay una función que lee el valor guardado y construye una consulta con él.
- El error o la diferencia de comportamiento aparece en una pantalla distinta de la de entrada.

## Procedimiento

1. Mapear los campos que se guardan y se muestran o procesan después.
2. Insertar un valor con una comilla simple y comprobar si el segundo paso falla o cambia.
3. Confirmar con una condición verdadera y otra falsa.
4. Construir una UNION con el número de columnas correcto.
5. Extraer hashes, correos o tokens y reutilizarlos.

## Comandos

```text
usuario: test' AND 1=1-- -
usuario: test' AND 1=2-- -
```

```sql
' UNION SELECT 1,username,password,4,5 FROM users-- -
```

```bash
sqlmap -u "https://<HOST>/<RUTA>" --data="username=<PAYLOAD>&password=x" --batch --dump
```

## Variantes

- Guardar el payload en el registro y disparar la consulta con un login posterior.
- Inyectar en un campo que se usa como nombre de tabla o de columna.
- Combinar con un cambio de contraseña o de rol para observar el efecto.
- Si hay filtros, codificar el payload o usar funciones equivalentes.

## Limitaciones

- El número de columnas y los tipos deben coincidir con la consulta destino.
- La aplicación puede escapar en el segundo paso aunque no lo haga en el primero.
- El efecto puede requerir privilegios o un flujo concreto.
- Los logs pueden conservar el payload almacenado.

## Mitigación

- Parametrizar todas las consultas, también las que leen datos ya guardados.
- Validar y normalizar los campos en la entrada y en la salida.
- Usar un ORM con consultas preparadas y evitar SQL dinámico.
- Limitar los privilegios de la cuenta de base de datos.
- Revisar los flujos que reutilizan datos de usuario en consultas.

## Detección

- Comillas, comentarios SQL y `UNION` en campos almacenados.
- Errores SQL en pantallas distintas de la de entrada.
- Consultas con concatenación de valores que vienen de la base.
- Diferencias de comportamiento entre registros con y sin payload.

## Referencias

- [OWASP — SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [PortSwigger — Second-order SQL injection](https://portswigger.net/web-security/sql-injection)
- [0xdf — EarlyAccess](https://0xdf.gitlab.io/2022/02/12/htb-earlyaccess.html)
- [Ficha EarlyAccess](../../machines/linux/earlyaccess/README.md)
