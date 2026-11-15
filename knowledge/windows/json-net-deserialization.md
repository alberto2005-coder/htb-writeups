---
topic: Json.Net — deserialización de Bearer con TypeNameHandling
tags: [windows, dotnet, json.net, deserialization, ysoserial]
---

# Json.Net — deserialización de Bearer con TypeNameHandling

[🇬🇧 English](json-net-deserialization.en.md) | **Español**

## Concepto

Newtonsoft.Json puede incluir el tipo .NET en el JSON mediante `$type` cuando `TypeNameHandling` no es `None`. Si un endpoint deserializa el token Bearer o una cookie con esa configuración, un objeto con un gadget de `ysoserial.net` ejecuta código durante la construcción.

## Cuándo aplica

- La aplicación usa Json.Net para tokens, cookies o cuerpos de API.
- `TypeNameHandling` es `All`, `Objects` o `Auto`.
- El ensamblado con el gadget está disponible en el servidor.

## Procedimiento

1. Decodificar el token y comprobar si acepta JSON con `$type`.
2. Generar un payload con el gadget `WindowsIdentity` y el formatter `Json.Net`.
3. Enviarlo en el Bearer, cookie o campo deserializado.
4. Observar la ejecución y lanzar una reverse shell.

```bash
ysoserial.exe -g WindowsIdentity -f Json.Net -c "whoami" -o base64
```

```text
Authorization: Bearer <BASE64>
```

## Variantes

- Gadget `ObjectDataProvider` con `Json.Net`.
- `TypeNameHandling=Auto` en un campo anidado.
- `JsonConvert.DeserializeObject` sobre el cuerpo completo de una petición.

## Limitaciones

- `TypeNameHandling=None` bloquea el ataque.
- El gadget debe existir y ser cargable.
- Un WAF puede bloquear `$type` o el base64 con firmas conocidas.

## Mitigación

- Usar `TypeNameHandling.None` y DTOs concretos.
- Validar el token en un servidor que no deserialice tipos arbitrarios.
- Firmar y cifrar el token; no confiar en su contenido.

## Detección

- Peticiones con `$type` o base64 que decodifica a JSON con `$type`.
- Procesos hijos de `w3wp.exe` o del servicio .NET.
- Errores de deserialización con nombres de ensamblados.

## Referencias

- [0xdf — Json](https://0xdf.gitlab.io/2020/02/15/htb-json.html)
- [ysoserial.net — Json.Net formatter](https://github.com/pwntester/ysoserial.net)
- [Newtonsoft — TypeNameHandling](https://www.newtonsoft.com/json/help/html/T_Newtonsoft_Json_TypeNameHandling.htm)
