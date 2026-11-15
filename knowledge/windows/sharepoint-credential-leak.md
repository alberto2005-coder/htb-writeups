---
topic: Credenciales expuestas en SharePoint
tags: [windows, sharepoint, credentials, enumeration, ftp]
---

# Credenciales expuestas en SharePoint

[🌐 English](sharepoint-credential-leak.en.md) | **Español**

## Concepto

SharePoint indexa listas, páginas, wikis y documentos que a veces contienen credenciales de otros servicios. La enumeración de sitios y la búsqueda de cadenas permite recolectar usuarios, contraseñas y rutas internas.

## Cuándo aplica

- SharePoint accesible con permisos de lectura amplios.
- Listas de inventario, guías o páginas de proyecto.
- Documentos que referencian FTP, SMB o bases de datos.

## Procedimiento

1. Enumerar sitios, listas y bibliotecas accesibles.
2. Buscar términos como `password`, `ftp`, `connectionString` o `creds`.
3. Descargar documentos y revisar metadatos y comentarios.
4. Probar las credenciales contra el servicio indicado.

```bash
curl -s http://<HOST>/_api/web/webs
curl -s 'http://<HOST>/_api/search/query?querytext=%27password%27'
# Descargar listas o bibliotecas accesibles y buscar cadenas
curl -s http://<HOST>/sites/<SITE>/Shared%20Documents/
```

## Variantes

- Listas personalizadas con columnas ocultas.
- Versiones antiguas de documentos.
- Comentarios y metadatos de Office.
- Permisos de invitado que exponen sitios internos.

## Limitaciones

- Se necesita acceso de lectura al sitio.
- La búsqueda puede estar deshabilitada.
- Las credenciales pueden estar caducadas.

## Mitigación y detección

- Revisar permisos y aplicar mínimo privilegio en SharePoint.
- No almacenar secretos en listas, páginas ni documentos.
- Rotar credenciales y monitorizar búsquedas y descargas masivas.

## Referencias

- <https://learn.microsoft.com/en-us/sharepoint/security-for-sharepoint-server/security-for-sharepoint-server>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview>
