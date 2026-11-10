---
sherlock: Lockpick
domain: Análisis de malware
difficulty: Easy
platform: Hack The Box
evidence: Muestra de ransomware, ficheros cifrados y nota de rescate
tools: [IDA, Ghidra, strings, CyberChef]
state: Retired
tags: [dfir, malware, ransomware, linux, analisis-estatico]
---

# Lockpick — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Investigación defensiva. Sin respuestas literales de la plataforma.

## Escenario

Forela se niega a pagar: una parte de sus servidores UNIX ha quedado cifrada y hay que recuperar los ficheros analizando la muestra. El ZIP trae un `DANGER.txt` con la contraseña del propio ZIP y la advertencia de manipular el binario sólo en una VM aislada.

## Evidencias

- `DANGER.txt` (contraseña del ZIP y aviso).
- El binario de ransomware, sin empaquetar.
- Un directorio con ficheros cifrados.

## Investigación

1. **Triage**: hash y tipo; es un ELF de Linux, no un PE.

```bash
md5sum lockpick; file lockpick; strings -n 8 lockpick | head -40
```

2. **Flujo de cifrado**: en IDA/Ghidra, `main` recorre un directorio y llama a `encrypt_file(ruta, clave)`. La clave **está embebida en el binario**, no se negocia con un servidor: por eso la recuperación es posible sin pagar.

3. **Clave y algoritmo**: la pregunta del caso es literalmente la cadena de clave. Se localiza en la función de cifrado (o con `strings` si no está ofuscada) y se confirma qué rutina la usa.

4. **Descifrar**: se reproduce el inverso (AES en modo ECB/CBC según lo que muestre el desensamblado) sobre una copia de los ficheros, y se valida con la cabecera conocida del original.

```python
from Crypto.Cipher import AES
# clave extraída del binario; el modo y el padding deben coincidir con los del sample
```

5. **Integridad**: el caso pide el MD5 de un fichero ya descifrado (`complaints.csv` en los writeups públicos) para confirmar que la recuperación es correcta.

## Hallazgos

- Ransomware **ELM/ELF para UNIX** con clave simétrica estática embebida.
- Sin infraestructura de C2 ni material asimétrico: el cifrado es reversible con la muestra.
- El `DANGER.txt` es parte de la cadena de custodia: contraseña del ZIP y advertencia de aislamiento.

## Lecciones

- `file` + `strings` resuelven el triage antes de abrir el desensamblador.
- Una clave estática en el binario es el peor diseño posible para el atacante: el descifrado se automatiza.
- El hash del fichero recuperado es la prueba de que el inverso está bien implementado.

## Tropiezos

- **Ejecutar la muestra**: siempre VM aislada y sin red.
- **Modo y padding**: un IV o un modo distintos producen basura; comprobar con el primer bloque.
- **Confundir cifrado con codificación**: aquí hay criptografía real con clave embebida, no base64.
