---
topic: Rails Redis deserialization
tags: [web, rails, redis, deserialization, cve-2020-8164]
---

# Rails Redis deserialization

[🌐 Español](rails-redis-deserialization.md) | **English**

## Concept

Rails stores session or user data in Redis and rebuilds it with `Marshal.load`. If an attacker controls the value, they can send a serialized object that executes code during deserialization. CVE-2020-8164/8165 affect old Rails versions.

## When it applies

- Rails < 5.2.4.3 or < 6.0.3.1 with `RedisCacheStore`/`MemCacheStore`.
- User values stored and read without signing.
- Source code or GitWeb access to locate the entry point.

## Procedure

1. Review `Gemfile.lock` and controllers using Redis.
2. Build a `Marshal.dump` of an object wrapping `ERB` and a command.
3. Send it in the parameter stored in Redis.
4. Confirm with a harmless request before a shell.

```ruby
code = '`id`'
erb = ERB.allocate
erb.instance_variable_set(:@src, code)
payload = Marshal.dump(ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erb, :result))
```

## Variants

- Direct `Marshal.load` on cookies.
- `YAML.load` with permitted objects.
- `ActiveSupport::Deprecation` as a gadget.
- Unauthenticated Redis used to inject the value.

## Limitations

- The Rails version must be vulnerable.
- The value must reach `Marshal.load`.
- Gadgets depend on installed gems.

## Mitigation and detection

- Update Rails and never deserialize untrusted input.
- Sign or encrypt cookies and session values.
- Authenticate Redis and isolate it from the network.
- Alert on `Marshal` objects and commands in parameters.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2020-8164>
- <https://nvd.nist.gov/vuln/detail/CVE-2020-8165>
- <https://guides.rubyonrails.org/security.html>
