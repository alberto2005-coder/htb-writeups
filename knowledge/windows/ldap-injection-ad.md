---
topic: LDAP — inyección de filtros en Active Directory
tags: [windows, active-directory, ldap, inyeccion, enumeracion, analysis]
---

# LDAP — inyección de filtros en Active Directory

[🌐 English](ldap-injection-ad.en.md) | **Español**

## Concepto

LDAP se usa para consultar directorios como Active Directory. Cuando una aplicación concatena la entrada del usuario en un filtro, los metacaracteres `(`, `)`, `*`, `\` y `|` alteran la lógica de la consulta. La inyección permite ampliar resultados, enumerar atributos y, si la aplicación muestra datos, leer campos como `description` o `info`, donde a veces hay contraseñas. En Analysis, el parámetro `name` de un buscador interno permitía enumerar usuarios y leer la contraseña de una cuenta compartida.

## Cuándo aplica

- Una aplicación web autentica o busca usuarios contra AD por LDAP.
- El parámetro se refleja en el filtro sin escapar.
- La respuesta cambia al introducir `*` o paréntesis.
- La cuenta usada por la aplicación tiene permisos de lectura sobre atributos sensibles.

## Procedimiento

1. Confirmar el comportamiento con `*`, `)(` y valores vacíos.
2. Ajustar el filtro para devolver todos los objetos o un atributo concreto.
3. Enumerar usuarios, grupos y atributos visibles.
4. Leer `description`, `info`, `comment` y campos similares.
5. Reutilizar las credenciales encontradas en el panel, SMB, WinRM o VPN.

## Comandos

```text
name=*
name=*)(objectClass=user)(cn=*
name=*)(description=*
name=admin)(|(description=*
```

```bash
ldapsearch -x -H ldap://<DC> -D '<USER>@<DOMAIN>' -w '<PASSWORD>' \
  -b 'DC=<DOMAIN>,DC=<TLD>' '(objectClass=user)' description
```

## Variantes

- Inyección en el filtro de autenticación para saltarse la contraseña.
- Inyección ciega por diferencias de tiempo o de código de estado.
- Uso de `*` para fuerza bruta de usuarios y atributos.
- Consultas a `LDAP://` desde PowerShell para repetir la enumeración.
- Aprovechamiento de atributos con contraseñas de cuentas de servicio.

## Limitaciones

- El servidor puede escapar los metacaracteres o usar consultas parametrizadas.
- La cuenta de la aplicación puede tener permisos mínimos.
- Los atributos sensibles pueden estar restringidos por ACL.
- La inyección no siempre devuelve datos; a veces solo cambia el número de resultados.
- Las consultas quedan registradas en el controlador de dominio.

## Mitigación

- Parametrizar las consultas LDAP y escapar los metacaracteres.
- Aplicar listas de permitidos a los atributos que se pueden consultar.
- No guardar contraseñas en `description` ni en atributos legibles.
- Usar cuentas de servicio con permisos mínimos y auditoría.
- Revisar los filtros construidos dinámicamente en el código.

## Detección

- Peticiones con `*`, `)(`, `|` o paréntesis desbalanceados en parámetros de búsqueda.
- Consultas LDAP que devuelven más objetos de los esperados.
- Lecturas de `description` o `info` desde cuentas web.
- Errores de LDAP expuestos al usuario.
- Picos de enumeración de usuarios seguidos de intentos de autenticación.

## Referencias

- [0xdf — Analysis](https://0xdf.gitlab.io/2024/06/01/htb-analysis.html)
- [OWASP — LDAP Injection](https://owasp.org/www-community/attacks/LDAP_Injection)
- [Microsoft — LDAP filters](https://learn.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax)
- [Ficha Analysis](../../machines/windows/analysis/README.md)
