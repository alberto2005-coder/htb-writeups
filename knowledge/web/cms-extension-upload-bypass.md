---
topic: Bypass de listas negras en subidas CMS
tags: [web, cms, upload, blacklist, php]
---

# Bypass de listas negras en subidas CMS

[🌐 English](cms-extension-upload-bypass.en.md) | **Español**

## Concepto

Un CMS bloquea `.php`, `.phtml` y otras extensiones, pero olvida variantes que el servidor sigue interpretando como PHP (`.php5`, `.php7`, `.phar`). La lista negra no cubre el mapa real de handlers de Apache.

## Cuándo aplica

- Gestores de medios con lista negra de extensiones.
- Apache con `AddHandler`/`SetHandler` para PHP.
- Directorios de subida servidos públicamente.

## Procedimiento

1. Identificar el CMS y su versión.
2. Enumerar extensiones bloqueadas y permitidas.
3. Probar una extensión alternativa con un PHP inocuo.
4. Verificar la ruta pública y la ejecución.

```bash
printf '<?php echo 7*7; ?>' > test.php5
curl -s -F "file=@test.php5" http://<HOST>/upload
curl -s http://<HOST>/uploads/test.php5
```

## Variantes

- `.pht`, `.phtm`, `.phar`, `.inc`.
- Doble extensión `file.php.jpg` con configuración laxa.
- Mayúsculas o punto final en Windows.
- `.htaccess` para mapear una extensión.

## Limitaciones

- El servidor debe interpretar la extensión.
- La ruta de subida debe ser accesible.
- Los filtros de contenido pueden bloquear el payload.

## Mitigación y detección

- Usar listas blancas y renombrar archivos.
- Servir subidas desde un dominio sin ejecución.
- Deshabilitar handlers PHP en directorios de usuario.
- Alertar de subidas con extensiones PHP poco comunes.

## Referencias

- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://www.exploit-db.com/exploits/41936>
- <https://attack.mitre.org/techniques/T1505/003/>
