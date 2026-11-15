---
topic: PHP — ejecución después de una redirección
tags: [web, php, execute-after-redirect, auth-bypass]
---

# PHP — ejecución después de una redirección

[🌐 English](execute-after-redirect.en.md) | **Español**

## Concepto

Si el código envía `Location` pero no llama a `exit`, PHP sigue ejecutando el resto del script. Un atacante puede interceptar el 302 y cambiar la respuesta para ver el contenido protegido o realizar acciones autenticadas.

## Cuándo aplica

- El control de sesión hace `header('Location: ...')` sin `exit`.
- El cuerpo de la página protegida se genera después.
- Se puede interceptar la respuesta con un proxy.

## Procedimiento

1. Solicitar la página protegida sin sesión.
2. Interceptar el 302 y cambiarlo a 200.
3. Leer el formulario o ejecutar la acción.
4. Crear un usuario o extraer datos.

## Comandos

```bash
# Burp: interceptar response 302 y cambiar a 200 OK
curl -i http://<HOST>/accounts.php
```

## Variantes

- Redirección en JavaScript.
- `die()` mal colocado.
- Acciones POST protegidas solo por el redirect.

## Limitaciones

- El servidor puede no enviar el cuerpo.
- El proxy debe reescribir la respuesta.
- La sesión puede validarse antes de la acción.

## Mitigación

- Llamar a `exit`/`die` tras la redirección.
- Aplicar el control de acceso antes de generar la página.
- Usar un framework con middleware.

## Detección

- Respuestas 302 con cuerpo de página protegida.
- Acciones sin sesión desde el mismo cliente.
- Peticiones con 302 modificado.

## Referencias

- [0xdf — Previse](https://0xdf.gitlab.io/2022/01/08/htb-previse.html)
- [OWASP — Execution after redirect](https://owasp.org/www-community/attacks/Execution_After_Redirect_(EAR))
- [PHP — header](https://www.php.net/manual/en/function.header.php)
