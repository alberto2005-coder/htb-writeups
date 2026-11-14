---
topic: JSF ViewState — deserialización Java
tags: [web, java, jsf, viewstate, deserialization]
---

# JSF ViewState — deserialización Java

[🌐 English](jsf-viewstate-deserialization.en.md) | **Español**

## Concepto

JavaServer Faces envía el estado de la vista en `javax.faces.ViewState`. Si el servidor lo deserializa sin cifrar ni firmar, un objeto serializado malicioso puede ejecutar código mediante una cadena de gadgets.

## Cuándo aplica

- Aplicaciones JSF/MyFaces o Mojarra con ViewState en Base64.
- Parámetros `javax.faces.ViewState` grandes o con prefijo `rO0AB`.
- Servidores con librerías Java vulnerables en el classpath.

## Procedimiento

1. Capturar el parámetro `ViewState` de un POST.
2. Decodificarlo y comprobar la firma `rO0AB` de Java serializado.
3. Identificar la librería y la versión de JSF.
4. Generar una cadena de gadgets compatible.
5. Reemplazar el ViewState y enviar la petición.

## Comandos

```bash
echo '<VIEWSTATE>' | base64 -d | xxd | head
java -jar ysoserial.jar CommonsCollections5 'id' | base64 -w0
```

## Variantes

- ViewState cifrado con una clave conocida o por defecto.
- Mojarra con `ViewState` comprimido o encriptado.
- Deserialización en cookies o parámetros de sesión.

## Limitaciones

- El ViewState puede estar firmado o cifrado.
- La cadena de gadgets debe existir en el classpath.
- Los WAF pueden bloquear payloads Base64 grandes.

## Mitigación

- Configurar `ViewState` firmado y cifrado.
- Actualizar JSF y las librerías Java.
- Evitar deserializar datos controlados por el usuario.

## Detección

- ViewState con firmas `rO0AB` inesperadas o tamaños anómalos.
- Errores de deserialización y procesos Java lanzando comandos.

## Referencias

- <https://community.owasp.org/vulnerabilities/Deserialization_of_untrusted_data>
- <https://attack.mitre.org/techniques/T1190/>
