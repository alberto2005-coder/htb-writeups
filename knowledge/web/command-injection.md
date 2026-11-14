---
topic: Command injection
tags: [web, command-injection, rce, blind, commix, shell]
---

# Command injection

[🌐 English](command-injection.en.md) | **Español**

## Concepto

La inyección de comandos ocurre cuando una aplicación pasa entrada del usuario a una shell sin separar argumentos ni validar caracteres. Puede ser directa, si el resultado se refleja, o ciega, si solo se observa tiempo, errores o efectos secundarios.

## Cuándo aplica

- Parámetros usados en `ping`, `nslookup`, `convert` o scripts.
- Formularios que ejecutan utilidades del sistema.
- Respuestas con salida de comandos.
- Funciones que permiten retardos o escritura de archivos.

## Procedimiento

1. Identificar el parámetro y el comando subyacente.
2. Probar separadores y sustituciones.
3. Confirmar con un comando inocuo.
4. Usar tiempo o DNS para casos ciegos.
5. Estabilizar la ejecución o el reverse shell.

```bash
curl -s 'http://<HOST>/ping?ip=127.0.0.1;id'
curl -s 'http://<HOST>/ping?ip=127.0.0.1%0aid'
curl -s 'http://<HOST>/ping?ip=127.0.0.1;sleep+5'
commix --url='http://<HOST>/ping?ip=127.0.0.1' --os-cmd=id
```

## Variantes

- Separadores `;`, `|`, `||`, `&&`, `$()` y backticks.
- Inyección ciega por tiempo o por DNS.
- Filtros que bloquean espacios o palabras clave.
- Inyección en argumentos de una herramienta de imagen o PDF.

## Limitaciones

- El comando puede ejecutarse en un contenedor.
- Los filtros pueden bloquear caracteres.
- La salida puede no reflejarse.
- El proceso puede tener pocos privilegios.

## Mitigación y detección

- Evitar shells y usar APIs con argumentos separados.
- Validar con listas permitidas y escapar.
- Ejecutar con mínimos privilegios y sin red.
- Alertar de procesos hijos, `sh -c` y patrones de separadores.

## Referencias

- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://attack.mitre.org/techniques/T1059/004/>
- <https://github.com/commixproject/commix>
