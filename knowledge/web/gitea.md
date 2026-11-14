---
topic: Gitea
tags: [web, gitea, git, repositories, credentials, source-code]
---

# Gitea

[🌐 English](gitea.en.md) | **Español**

## Concepto

Gitea es un servicio Git autoalojado que puede exponer repositorios, usuarios, tokens y configuraciones. Un repositorio accesible puede contener credenciales, claves, pipelines o código vulnerable; una cuenta con permisos puede modificar hooks o crear un runner.

## Cuándo aplica

- Instancia Gitea expuesta.
- Repositorios públicos o de invitado.
- Registro abierto.
- Tokens o claves en el historial.

## Procedimiento

1. Enumerar usuarios, organizaciones y repositorios.
2. Clonar repositorios accesibles y revisar el historial.
3. Buscar secretos en código, issues y releases.
4. Revisar hooks, runners y claves de despliegue.
5. Reutilizar credenciales contra otros servicios.

```bash
git clone http://<HOST>/<ORG>/<REPO>.git
git log --all --oneline
trufflehog git http://<HOST>/<ORG>/<REPO>.git
```

## Variantes

- Repositorio privado con acceso de invitado.
- Token de API en un archivo `.env`.
- Hook que ejecuta un comando en el servidor.
- Runner con acceso al host.

## Limitaciones

- El registro puede estar cerrado.
- Los repositorios pueden estar vacíos o ser señuelos.
- Los secretos pueden estar en ramas eliminadas.
- Los hooks requieren permisos de administrador.

## Mitigación y detección

- Restringir registro y visibilidad.
- Escanear secretos y rotar credenciales.
- Auditar hooks, runners y claves de despliegue.
- Alertar de clones masivos y cambios en integraciones.

## Referencias

- <https://docs.gitea.com/>
- <https://attack.mitre.org/techniques/T1213/003/>
- <https://github.com/trufflesecurity/trufflehog>
