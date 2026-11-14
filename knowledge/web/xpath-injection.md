---
topic: XPath injection
tags: [web, xpath, xml, injection, auth-bypass]
---

# XPath injection

[🌐 English](xpath-injection.en.md) | **Español**

## Concepto

Una consulta XPath construida concatenando la entrada del usuario permite alterar la selección de nodos. Se puede saltar la autenticación, enumerar el documento XML y extraer valores nodo a nodo.

## Cuándo aplica

- Login o buscador respaldado por XML.
- Parámetros que se reflejan en errores de XPath.
- Aplicaciones que validan usuarios contra un fichero XML.

## Procedimiento

1. Probar comillas simples y dobles y observar errores.
2. Intentar un bypass con `' or '1'='1`.
3. Determinar el número de nodos y la estructura.
4. Extraer cadenas con `substring` y comparaciones booleanas.
5. Reutilizar las credenciales encontradas.

## Comandos

```text
' or '1'='1
' or name()='user' or '1'='2
' or substring(//user[1]/password,1,1)='a' or '1'='2
```

## Variantes

- Inyección ciega por respuestas booleanas.
- Errores que revelan la ruta o el nombre del nodo.
- XPath sobre documentos subidos por el usuario.

## Limitaciones

- El parser puede escapar comillas.
- La consulta puede usar variables precompiladas.
- Los errores pueden estar ocultos.

## Mitigación

- Usar XPath parametrizado o variables.
- Validar y normalizar la entrada.
- No mostrar errores del parser.

## Detección

- Comillas y operadores booleanos en parámetros.
- Errores de XPath y consultas anómalas.

## Referencias

- <https://owasp.org/www-community/attacks/XPATH_Injection>
- <https://attack.mitre.org/techniques/T1190/>
