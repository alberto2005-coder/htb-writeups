---
challenge: Hidden in Colors
type: Stego
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [stego, imagen, png, colores, hex, mapeo]
---

# Hidden in Colors — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Reto resuelto; sin flags reales.

## TL;DR

La imagen no esconde datos en los bits menos significativos: **el propio valor de color de cada píxel es el dato**. Los colores están elegidos de forma artificial (pocos tonos, valores hexadecimales "demasiado limpios"), y el mensaje se recupera mapeando esos códigos de color a caracteres. Es un reto de **Stego Hard**, no un `zsteg` de un paso.

## Enunciado y superficie

"We intercepted this weird image coming from a…": se entrega una única imagen PNG. No hay contraseña ni aplicación; el artefacto es el binario entero del reto.

## Reconocimiento

```bash
file image.png
exiftool image.png
pngcheck -v image.png
zsteg -a image.png | head -30
```

Lo esperable: PNG válido, sin metadatos útiles y sin LSB legible. Si `zsteg` no devuelve texto, la hipótesis del LSB está descartada y toca mirar los **valores de color**.

## Explicación del fallo

Al abrir la imagen se ve un patrón de colores planos, no una foto. Los píxeles usan una paleta muy reducida y sus códigos hexadecimales (`#RRGGBB`) siguen una secuencia, no una distribución natural. Ese es el canal: **el dato está codificado en el color, no en el bit bajo**.

## Explotación

1. **Listar los colores** por frecuencia o en orden de aparición, con GIMP (cuentagotas + ventana de paleta), con la vista "Extract RGBA values" de StegOnline, o con Python:

```python
from PIL import Image
im = Image.open("image.png").convert("RGB")
seen, order = set(), []
for px in im.getdata():
    if px not in seen:
        seen.add(px); order.append(px)
print(len(order), order[:16])
```

2. **Mapear cada color a su valor**: si son pocos (decenas), cada color puede ser un carácter ASCII o un nibble; si son 256, cada color es directamente un byte `0xRRGGBB` reducido.

```python
codes = ["%02x%02x%02x" % px for px in order]
print("".join(chr(int(c, 16) % 256) for c in codes)[:200])
```

3. **Reconstruir el orden**: el mensaje suele leerse en el orden de barrido de la imagen (fila a fila); si el texto sale desordenado, probar orden de columnas o el inverso.

```python
data = "".join(chr(px[0]) for px in im.getdata() if px != (0, 0, 0))
print(data[:120])
```

4. **Verificar**: la salida debe empezar por el prefijo de la flag (`HTB{`). Cuando aparece, se ha encontrado el mapa correcto.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Descartar el LSB primero** con `zsteg -a`: si no hay texto, el canal es otro y no se pierde tiempo.
- **Los colores "bonitos" son una pista**: una paleta artificial delata codificación en el valor de color.
- **El orden importa**: un mapa correcto con un barrido incorrecto sigue dando basura.

- En Stego, la herramienta por defecto no es la respuesta por defecto.
- Una imagen de pocos colores planos es un fichero de datos disfrazado.
- Mitigación: no sirve aquí; en el mundo real, el canal encubierto se detecta por análisis de paleta y entropía, no por firmas.

## Nota de verificación

El reto es **Hard** en HTB y el walkthrough oficial trabaja el "mapeo de códigos de color hex"; no hay writeups públicos detallados de la solución paso a paso, así que los pasos anteriores describen la técnica, no una transcripción de la respuesta.
