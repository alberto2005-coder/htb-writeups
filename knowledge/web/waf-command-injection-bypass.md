---
topic: Bypass de WAF en inyección de comandos
tags: [web, waf, command-injection, bypass, lua]
---

# Bypass de WAF en inyección de comandos

[🌐 English](waf-command-injection-bypass.en.md) | **Español**

## Concepto

Un WAF filtra caracteres o palabras clave, pero la aplicación sigue concatenando entrada en un comando de shell. La sintaxis equivalente (comillas, variables, wildcards, codificación) permite ejecutar comandos sin usar los tokens bloqueados.

## Cuándo aplica

- Parámetros que llegan a `system`, `popen`, `exec` o `bash -c`.
- WAF con listas negras de `;`, `|`, `$`, `(`, `)`.
- Filtros que solo inspeccionan el User-Agent o la URL decodificada.

## Procedimiento

1. Confirmar la inyección con una expresión inocua.
2. Identificar los caracteres bloqueados y el contexto de comillas.
3. Romper el contexto con comillas simples y separar palabras con `''`.
4. Enviar la petición cruda si el cliente normaliza la URL.

```bash
curl "http://<HOST>/sync?opt=' id'"
curl "http://<HOST>/sync?opt=' c''at /etc/passwd'"
# Alternativas: ${IFS}, wildcards, variables, codificación doble
curl --path-as-is "http://<HOST>/sync?opt='%20id'"
```

## Variantes

- `$IFS` o `${IFS}` para espacios.
- `?`, `*` y comodines para rutas.
- Variables de entorno y expansión indirecta.
- Ofuscación Unicode o doble URL-encoding.

## Limitaciones

- El WAF puede normalizar y decodificar antes de comparar.
- El contexto de comillas debe ser explotable.
- La petición cruda puede requerir un cliente que no normalice.

## Mitigación y detección

- No construir comandos de shell con entrada externa; usar APIs con argumentos.
- Validar por listas blancas en el código, no confiar en el WAF.
- Registrar y alertar de patrones de inyección y procesos hijos anómalos.

## Referencias

- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://portswigger.net/web-security/os-command-injection>
- <https://attack.mitre.org/techniques/T1059/004/>
