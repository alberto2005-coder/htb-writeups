---
topic: WebAssembly — desbordamiento de buffer y XSS almacenado
tags: [web, wasm, buffer-overflow, xss, rails, memory]
---

# WebAssembly — desbordamiento de buffer y XSS almacenado

[🌐 English](wasm-buffer-overflow-xss.en.md) | **Español**

## Concepto

Un módulo WebAssembly escrito en C copia cadenas en buffers de tamaño fijo sin comprobar la longitud. Aunque WASM se ejecuta en un sandbox, el desbordamiento corrompe la memoria lineal del propio módulo: puede sobrescribir un campo contiguo que luego se inserta en el DOM. Si el valor sobrescrito contiene HTML, se convierte en XSS almacenado.

## Cuándo aplica

- La aplicación usa WASM para renderizar o procesar datos de usuario.
- El binario usa `strcpy`, `memcpy` o bucles sin límite.
- El resultado del módulo se inserta con `innerHTML` o plantillas sin escapar.
- El usuario puede registrarse o publicar contenido que revisa un administrador.

## Procedimiento

1. Localizar el módulo `.wasm` y las funciones exportadas.
2. Identificar los buffers y sus offsets (herramientas como `wasm2wat` o Ghidra).
3. Enviar una cadena larga y observar qué campo cambia.
4. Colocar el HTML en el offset exacto y publicar el contenido.
5. Esperar a que el bot o el administrador cargue la página.

## Comandos

```bash
wasm2wat app.wasm -o app.wat
# buscar llamadas a memory.copy / memory.fill y tamaños fijos
python3 -c 'print("A"*48 + "<img src=x onerror=alert(1)>")'
```

## Variantes

- Sobrescribir una fecha, un nombre o un contador que se pinta después.
- Usar el desbordamiento para cambiar una decisión de control.
- Combinarlo con un `fetch` que cargue un script externo.
- XSS que exfiltra el HTML del panel de administración.

## Limitaciones

- El offset depende de la compilación y del asignador.
- WASM no permite salir del sandbox del navegador.
- El campo debe acabar en el DOM sin escape.
- El bot debe visitar el contenido.

## Mitigación

- Usar funciones con límite de longitud (`strlcpy`, `snprintf`).
- Validar y recortar en el servidor.
- Escapar la salida y usar `textContent`.
- Compilar con `-fsanitize=address` en desarrollo.

## Detección

- Cadenas anormalmente largas en registros y formularios.
- HTML en campos que deberían ser fechas o números.
- Peticiones del bot a dominios externos.
- Errores de memoria o reinicios del módulo.

## Referencias

- [MDN — WebAssembly](https://developer.mozilla.org/en-US/docs/WebAssembly)
- [OWASP — XSS](https://owasp.org/www-community/attacks/xss/)
- [0xdf — Derailed](https://0xdf.gitlab.io/2023/07/22/htb-derailed.html)
