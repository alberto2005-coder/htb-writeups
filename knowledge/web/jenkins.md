---
topic: Jenkins
tags: [web, jenkins, groovy, ci-cd, credentials, rce]
---

# Jenkins

[🌐 English](jenkins.en.md) | **Español**

## Concepto

Jenkins expone trabajos, credenciales y una consola Groovy que puede ejecutar código en el servidor. Una instancia sin autenticación, con credenciales débiles o con permisos de script permite comprometer el CI/CD y los secretos que gestiona.

## Cuándo aplica

- Panel `/manage` o `/script` accesible.
- Credenciales por defecto o usuario invitado.
- Trabajos con parámetros y scripts.
- Agentes con acceso a repositorios o producción.

## Procedimiento

1. Enumerar versión, plugins y trabajos.
2. Probar credenciales por defecto.
3. Revisar la consola de scripts.
4. Ejecutar un comando inocuo para confirmar.
5. Extraer credenciales y mover el acceso al CI/CD.

```bash
curl -s http://<HOST>:8080/api/json?tree=jobs[name,url]
curl -s --user "$JENKINS_AUTH" http://<HOST>:8080/script
```

## Variantes

- Consola Groovy sin autenticación.
- `jenkins-cli` con clave de usuario.
- Credenciales en trabajos o variables.
- Agente comprometido con acceso a la red interna.

## Limitaciones

- La consola puede requerir administrador.
- CSRF puede bloquear peticiones.
- Los agentes pueden estar aislados.
- Los secretos pueden estar enmascarados.

## Mitigación y detección

- Actualizar Jenkins y plugins.
- Deshabilitar la consola para usuarios no administradores.
- Aplicar MFA y mínimos privilegios.
- Auditar scripts, trabajos y accesos a credenciales.

## Referencias

- <https://www.jenkins.io/doc/book/security/>
- <https://attack.mitre.org/techniques/T1195/>
- <https://owasp.org/www-project-top-ten/>
