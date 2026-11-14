---
topic: Deserialización Rails desde Redis
tags: [web, rails, redis, deserialization, cve-2020-8164]
---

# Deserialización Rails desde Redis

[🌐 English](rails-redis-deserialization.en.md) | **Español**

## Concepto

Rails guarda datos de sesión o usuario en Redis y los reconstruye con `Marshal.load`. Si un atacante controla el valor, puede enviar un objeto serializado que ejecute código al deserializarse. CVE-2020-8164/8165 afectan a versiones antiguas de Rails.

## Cuándo aplica

- Rails < 5.2.4.3 o < 6.0.3.1 con `RedisCacheStore`/`MemCacheStore`.
- Valores de usuario almacenados y leídos sin firma.
- Acceso al código fuente o a GitWeb para localizar el punto de entrada.

## Procedimiento

1. Revisar `Gemfile.lock` y controladores que usan Redis.
2. Construir un `Marshal.dump` de un objeto con `ERB` y comando.
3. Enviarlo en el parámetro que se almacena en Redis.
4. Confirmar con una petición inocua antes de una shell.

```ruby
code = '`id`'
erb = ERB.allocate
erb.instance_variable_set(:@src, code)
payload = Marshal.dump(ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erb, :result))
```

## Variantes

- `Marshal.load` directo sobre cookies.
- `YAML.load` con objetos permitidos.
- `ActiveSupport::Deprecation` como gadget.
- Redis accesible sin autenticación para inyectar el valor.

## Limitaciones

- La versión de Rails debe ser vulnerable.
- El valor debe llegar a `Marshal.load`.
- Los gadgets dependen de las gemas instaladas.

## Mitigación y detección

- Actualizar Rails y no deserializar entrada no confiable.
- Firmar o cifrar cookies y valores de sesión.
- Autenticar Redis y aislarlo de la red.
- Alertar de objetos `Marshal` y de comandos en parámetros.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2020-8164>
- <https://nvd.nist.gov/vuln/detail/CVE-2020-8165>
- <https://guides.rubyonrails.org/security.html>
