---
challenge: Anti Flag
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, rc4, anti-debug, ghidra]
---

# Anti Flag — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El binario comprueba la entrada y esconde la flag en datos cifrados con RC4. El análisis estático localiza la llamada de descifrado y la clave embebida; desencriptar el bloque de `.rodata` revela la flag sin ejecutar el binario.

## Enunciado y superficie

- Reversing, Easy, retirado.
- Se entrega un ELF de 64 bits.
- El binario tiene comprobaciones anti-debug y compara la entrada.

```bash
file anti_flag
checksec --file=anti_flag
strings -a anti_flag | head
```

## Reconocimiento

- El binario no está stripped.
- `main` llama a una rutina de inicialización de RC4.
- La clave aparece como cadena o se construye en la pila.
- Hay llamadas a `ptrace` o comprobaciones de `TracerPid`.

## Análisis del código

En Ghidra/Binary Ninja se identifica la función RC4: KSA de 256 bytes, PRGA y XOR con el ciphertext. La clave `<KEY>` se pasa a la rutina y el bloque cifrado está en `.rodata` en `0x2011`.

## Explicación del fallo

La "protección" es ofuscación, no criptografía segura: la clave está en el binario y el algoritmo es reversible. Las comprobaciones anti-debug solo impiden la ejecución dinámica, no el análisis estático.

## Reproducción local

```bash
# Extraer los bytes cifrados y la clave
python3 - <<'PY'
from binascii import unhexlify
ct = unhexlify('<CIPHERTEXT>')
print(ct)
PY
```

## Explotación

```python
from Crypto.Cipher import ARC4
ct = bytes.fromhex('<CIPHERTEXT>')
print(ARC4.new(b'<KEY>').decrypt(ct))
```

También se puede usar la transformación RC4 de CyberChef o Binary Ninja. La flag se redacta.

## Evidencia

- `file`/`checksec` y cadenas relevantes.
- Función RC4 identificada.
- Bloque cifrado y clave localizados.
- Texto claro sin publicar la flag.

## Lecciones aprendidas

- RC4 con clave embebida es ofuscación reversible.
- El análisis estático evita las trampas anti-debug.
- Las cadenas de la clave pueden estar construidas en la pila.

## Mitigaciones y detección

- No almacenar secretos en binarios distribuidos.
- Usar cifrado autenticado y claves externas si se necesita protección.
- Detectar `ptrace` y binarios que leen `/proc/self/status`.
- Referencias: NIST RC4, HTB Anti Flag, MITRE T1027.

## Referencias

- <https://www.hackthebox.com/challenges/Anti%20Flag>
- <http://www.0xface1e55.com/posts/reversing/htb/anti_flag>
- <https://attack.mitre.org/techniques/T1027/>
- <https://attack.mitre.org/techniques/T1622/>
