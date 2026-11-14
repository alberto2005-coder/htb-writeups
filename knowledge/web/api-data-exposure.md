---
topic: Exposición de datos en APIs
tags: [web, api, data-exposure, hashes, backups, enumeration]
---

# Exposición de datos en APIs

[🌐 English](api-data-exposure.en.md) | **Español**

## Concepto

Una API devuelve más campos de los necesarios o sirve objetos que deberían ser internos. Un endpoint de usuarios puede incluir hashes, tokens, correos, roles o rutas de backup. El problema no es solo el acceso, sino la cantidad y sensibilidad de lo devuelto.

## Cuándo aplica

- Endpoints JSON de usuarios, pedidos o configuraciones.
- Respuestas que incluyen `password`, `hash`, `token`, `internal_id` o `path`.
- Directorios de backup accesibles desde la raíz web.
- APIs sin control de campos por rol.

## Procedimiento

1. Enumerar rutas y métodos con `ffuf`, `feroxbuster` o el histórico del navegador.
2. Revisar cada respuesta y anotar campos sensibles.
3. Comparar la respuesta de un usuario normal con la de un administrador.
4. Buscar archivos de backup y metadatos en rutas comunes.
5. Probar si los hashes son crackeables o reutilizables.

```bash
curl -s https://<HOST>/api/users/latest | jq '.[0] | keys'
curl -s -o /dev/null -w '%{http_code} %{size_download}\n' https://<HOST>/backup.zip
```

## Variantes

- Hash de contraseña en la respuesta y crackeo offline.
- Ruta de backup que contiene el código y credenciales.
- Campo `role` o `is_admin` manipulable.
- Enumeración secuencial de IDs sin autorización.

## Limitaciones

- El hash debe ser de un algoritmo débil o reutilizado.
- Los backups pueden estar fuera del directorio web.
- Algunos campos solo aparecen con parámetros concretos.
- Rate limiting y autenticación pueden frenar la enumeración.

## Mitigación y detección

- Usar DTOs y listas de campos permitidos por rol.
- Nunca devolver hashes, tokens ni rutas internas.
- Guardar backups fuera de la raíz web y protegerlos con autenticación.
- Alertar de descargas de ZIP/SQL y de enumeración de usuarios.

## Referencias

- <https://owasp.org/www-project-api-security/>
- <https://cwe.mitre.org/data/definitions/213.html>
- <https://attack.mitre.org/techniques/T1213/>
- <https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html>
