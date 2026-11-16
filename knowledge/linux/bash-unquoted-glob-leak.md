---
topic: Bash — comparación sin comillas y fuga por glob
tags: [linux, bash, glob, wildcard, secret-leak, privesc]
---

# Bash — comparación sin comillas y fuga por glob

[🌐 English](bash-unquoted-glob-leak.en.md) | **Español**

## Concepto

En `[[ $secreto == $entrada ]]`, si `$entrada` no va entre comillas, Bash la trata como patrón. Un `*` al final permite comprobar prefijos y filtrar un secreto carácter a carácter sin leerlo directamente.

## Cuándo aplica

- Un script privilegiado compara un secreto con una entrada controlada.
- La variable de entrada no está entre comillas.
- El script devuelve un mensaje distinto según la coincidencia.

## Procedimiento

1. Localizar la comparación y el mensaje de éxito.
2. Probar un prefijo conocido más `*`.
3. Iterar sobre el alfabeto y quedarse con el carácter que cambia la respuesta.
4. Repetir hasta reconstruir el secreto.

## Comandos

```bash
# archivo de entrada con el prefijo y un wildcard
printf '%s*' "$PREFIX" > /dev/shm/file
sudo /opt/check.sh /dev/shm/file
# repetir por carácter y comprobar el mensaje de éxito
```

## Variantes

- Patrones `?` para un carácter.
- Clases `[a-z]`.
- Comparaciones con `=`, `==` o `!=`.

## Limitaciones

- La variable puede estar citada.
- El script puede no revelar el resultado.
- Bash moderno mantiene el globbing en `[[ ]]`.

## Mitigación

- Citar siempre las variables en comparaciones.
- Usar `case` o comparaciones literales.
- No comparar secretos en scripts accesibles.

## Detección

- Llamadas repetidas a un script con archivos de entrada.
- Uso de `*` o `?` en argumentos.
- Lecturas de la CA o de claves desde `/dev/shm`.

## Referencias

- [0xdf — Resource](https://0xdf.gitlab.io/2024/11/23/htb-resource.html)
- [Bash — pattern matching](https://www.gnu.org/software/bash/manual/html_node/Pattern-Matching.html)
- [CWE-697 — Incorrect Comparison](https://cwe.mitre.org/data/definitions/697.html)
