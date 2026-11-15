---
topic: Inyección LaTeX
tags: [linux, latex, file-read, command-injection]
---

# Inyección LaTeX

[🌐 English](latex-injection.en.md) | **Español**

## Concepto

Un servicio que compila LaTeX con entrada del usuario puede permitir leer archivos con `\input` o `\lstinputlisting`. Si `shell-escape` está habilitado, también se pueden ejecutar comandos con `\write18`.

## Cuándo aplica

- La aplicación compila LaTeX o genera imágenes desde fórmulas.
- La entrada no está restringida a matemáticas.
- El motor tiene acceso a archivos del host.

## Procedimiento

1. Probar `\input{/etc/passwd}`.
2. Usar `\lstinputlisting` para archivos con caracteres especiales.
3. Leer configuración y credenciales.
4. Probar `\write18` si `shell-escape` está activo.

```latex
\input{/etc/passwd}
\lstinputlisting{/var/www/dev/.htpasswd}
\immediate\write18{id}
```

## Variantes

- Leer claves SSH o configuración de la aplicación.
- Escribir un archivo con `\newwrite`.
- Combinar con un LFI para alcanzar el motor.

## Limitaciones

- El motor debe permitir las primitivas.
- La ruta debe ser legible.
- `shell-escape` suele estar deshabilitado.

## Mitigación y detección

- Ejecutar LaTeX en un sandbox sin archivos.
- Deshabilitar `shell-escape` y limitar paquetes.
- Validar la entrada como matemáticas.

## Referencias

- <https://latex-project.org/>
- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://attack.mitre.org/techniques/T1059/004/>
