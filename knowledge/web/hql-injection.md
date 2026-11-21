---
topic: HQL — inyección en consultas Hibernate
tags: [web, hibernate, hql, inyeccion, java, fingerprint]
---

# HQL — inyección en consultas Hibernate

[🌐 English](hql-injection.en.md) | **Español**

## Concepto

Hibernate Query Language (HQL) consulta entidades Java, no tablas SQL. Cuando la aplicación concatena entrada del usuario en una consulta HQL, se pueden alterar las condiciones y extraer datos con inyección booleana. La sintaxis no es SQL: se usan nombres de entidades y propiedades, y los comentarios y funciones cambian. En Fingerprint, una consulta HQL construida con el nombre de usuario permitía enumerar registros y campos ocultos.

## Cuándo aplica

- Una aplicación Java con Hibernate construye HQL por concatenación.
- El parámetro se usa en `WHERE`, `ORDER BY` o `LIKE`.
- La respuesta cambia según la condición (boolean-based).
- Hay mensajes de error o diferencias de tiempo aprovechables.

## Procedimiento

1. Identificar la entidad y la propiedad usada en la consulta.
2. Probar comillas simples y operadores lógicos.
3. Confirmar con una condición verdadera y otra falsa.
4. Extraer datos carácter a carácter con `SUBSTRING` y comparaciones.
5. Ajustar mayúsculas y nombres de propiedades de la entidad.
6. Reutilizar los datos para autenticarse o escalar.

## Comandos

```text
' OR '1'='1
' AND SUBSTRING((SELECT u.password FROM User u WHERE u.username='admin'),1,1)='a'--
```

```bash
# Repetir la petición cambiando el carácter y medir la respuesta
ffuf -u 'http://<HOST>/<PATH>?q=<PAYLOAD>' -w chars.txt -mr '<TRUE_MARKER>'
```

## Variantes

- Inyección en `ORDER BY` para inferir columnas.
- Uso de funciones HQL como `SUBSTRING`, `LOWER`, `CONCAT` y `COALESCE`.
- Inyección ciega por tiempo con funciones de base de datos.
- Acceso a entidades relacionadas mediante navegación de propiedades.
- Combinación con deserialización o JWT para ejecutar código.

## Limitaciones

- HQL no acepta todas las construcciones SQL; hay que adaptar la sintaxis.
- Hibernate puede parametrizar o validar la consulta.
- Los errores pueden estar ocultos y la inyección ser solo ciega.
- Las entidades y propiedades deben conocerse o inferirse.
- Las consultas quedan en los logs de la aplicación.

## Mitigación

- Usar consultas parametrizadas (`setParameter`) y nunca concatenar entrada.
- Validar tipos y listas de permitidos para ordenación y filtros.
- No exponer errores de Hibernate al usuario.
- Revisar el código que construye HQL dinámicamente.
- Aplicar autorización por objeto en las consultas.

## Detección

- Parámetros con comillas, `OR`, `AND`, `SUBSTRING` o comentarios HQL.
- Consultas con tiempos de respuesta anómalos.
- Errores de Hibernate en respuestas HTTP.
- Accesos repetidos con variaciones de un solo carácter.
- Consultas que devuelven más entidades de las esperadas.

## Referencias

- [0xdf — Fingerprint](https://0xdf.gitlab.io/2022/05/14/htb-fingerprint.html)
- [Hibernate — HQL](https://docs.jboss.org/hibernate/orm/6.2/userguide/html_single/Hibernate_User_Guide.html#hql)
- [Ficha Fingerprint](../../machines/linux/fingerprint/README.md)
