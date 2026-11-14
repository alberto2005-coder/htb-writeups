---
topic: Extracción de binarios PyInstaller
tags: [forensics, pyinstaller, python, bytecode, reversing, malware]
---

# Extracción de binarios PyInstaller

[🌐 English](pyinstaller-extraction.en.md) | **Español**

## Concept

PyInstaller empaqueta un programa Python, sus dependencias y el intérprete en un solo ejecutable. El archivo contiene un archivo comprimido con el bytecode `.pyc`; se puede extraer y decompilar para recuperar la lógica, las claves y las cadenas.

## Cuándo aplica

- Ejecutables con cadenas de Python o referencias a `pyinstaller`.
- Malware escrito en Python.
- Herramientas internas distribuidas como binario.
- Retos de reversing y forensics.

## Procedimiento

1. Identificar el binario con `file` y `strings`.
2. Confirmar PyInstaller por las cadenas `MEI` o `pyi-`.
3. Extraer con `pyinstxtractor`.
4. Localizar el `.pyc` principal y ajustar la cabecera si falta.
5. Decompilar con `uncompyle6` o `decompyle3`.

```bash
python3 pyinstxtractor.py sample.exe
python3 -m uncompyle6 sample.exe_extracted/sample.pyc
```

## Variantes

- Bytecode sin cabecera mágica que requiere restaurarla.
- Versiones de Python sin decompilador directo.
- Cifrado de la clave con un loader nativo.
- Binarios de una sola etapa con recursos embebidos.

## Limitaciones

- La versión de Python debe ser compatible con el decompilador.
- El bytecode puede estar ofuscado o modificado.
- Los binarios recientes pueden incluir un loader que cifra la clave.
- La extracción no garantiza recuperar el código fuente exacto.

## Mitigación y detección

- No confiar en la opacidad del ejecutable como protección.
- Firmar binarios y verificar su origen.
- Analizar en sandbox antes de ejecutar.
- Alertar de procesos que extraen archivos temporales y lanzan Python.

## Referencias

- <https://github.com/extremecoders-re/pyinstxtractor>
- <https://pyinstaller.org/en/stable/operating-mode.html>
- <https://attack.mitre.org/techniques/T1027/009/>
- <https://attack.mitre.org/techniques/T1059/006/>
