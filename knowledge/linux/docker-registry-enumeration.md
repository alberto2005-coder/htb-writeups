---
topic: Docker Registry — enumeración y extracción de capas
tags: [linux, docker, registry, image, secrets]
---

# Docker Registry — enumeración y extracción de capas

[🌐 English](docker-registry-enumeration.en.md) | **Español**

## Concepto

Un registro Docker privado con credenciales débiles permite listar repositorios, descargar manifiestos y extraer capas. Las imágenes suelen contener claves SSH, contraseñas y configuración de despliegue.

## Cuándo aplica

- El registro responde en `/v2/`.
- Las credenciales son débiles o por defecto.
- Se puede descargar el manifiesto y sus blobs.

## Procedimiento

1. Listar `/v2/_catalog`.
2. Listar tags y descargar el manifiesto.
3. Extraer las capas y buscar secretos.
4. Usar las credenciales encontradas.

## Comandos

```bash
curl -k --user <USER>:<PASS> https://registry/v2/_catalog
curl -k --user <USER>:<PASS> https://registry/v2/<REPO>/tags/list
curl -k --user <USER>:<PASS> https://registry/v2/<REPO>/manifests/latest
```

## Variantes

- `docker pull` con `--tls-verify=false`.
- Blobs cacheados en `/var/lib/registry`.
- Autenticación básica en el proxy.

## Limitaciones

- El catálogo puede estar deshabilitado.
- Las capas pueden estar cifradas o firmadas.
- Las credenciales pueden ser de solo lectura.

## Mitigación

- Autenticación fuerte y TLS verificado.
- No incluir secretos en imágenes.
- Limitar el catálogo y auditar pulls.

## Detección

- Peticiones a `/v2/_catalog` desde hosts no habituales.
- Descargas masivas de blobs.
- Credenciales de registro usadas fuera del CI.

## Referencias

- [0xdf — Registry](https://0xdf.gitlab.io/2020/04/04/htb-registry.html)
- [Docker — Registry API](https://distribution.github.io/distribution/spec/api/)
- [Docker — security](https://docs.docker.com/engine/security/)
