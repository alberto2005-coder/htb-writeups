---
challenge: Sigma Technology
type: AI/ML
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ai, adversarial-ml, tensorflow, image-classification, evasion]
---

# Sigma Technology — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Un clasificador de imágenes acepta la modificación de cinco píxeles de un perro de 32×32. El objetivo es provocar una clasificación errónea hacia una clase que no sea animal. El fallo es un ejemplo de *adversarial machine learning*: pequeñas perturbaciones manipulables alteran la predicción.

## Enunciado y superficie

- Categoría AI/ML, dificultad Easy, retirado.
- Se entrega `sigmanet.h5` y `model.py`.
- Una web permite elegir posición y color RGB de cinco píxeles.
- El modelo clasifica en diez clases (avión, coche, pájaro, gato, ciervo, perro, rana, caballo, barco, camión).

```bash
curl -s -I http://<HOST>:<PORT>/
```

## Reconocimiento

- La imagen base es un perro de 32×32 píxeles.
- El modelo y el código de inferencia permiten reproducir la predicción localmente.
- La web solo devuelve la etiqueta y la confianza; no expone pesos ni gradientes.

```python
import imageio, numpy as np
img = np.array(imageio.imread("dog.png", pilmode="RGB"))
print(img.shape)
```

## Análisis

1. Cargar el modelo y comprobar que reproduce la clasificación original.
2. Generar cinco posiciones y colores aleatorios.
3. Evaluar la confianza de las clases no animales.
4. Conservar las mejores candidatas y mutar una posición o un canal.
5. Repetir hasta que la clase predicha sea `airplane`, `automobile`, `ship` o `truck`.
6. Enviar los cinco píxeles a la instancia remota.

```python
pred, conf = sigmanet.predict_one(modified_image)
score = max(conf[0][0], conf[0][1], conf[0][8], conf[0][9])
```

## Explicación del fallo

El modelo acepta entradas controladas por el usuario y la aplicación confía en su predicción sin comprobar la similitud con la imagen original. Una perturbación de cinco píxeles es suficiente para cruzar la frontera de decisión.

No se trata de un fallo de memoria ni de inyección: es una ausencia de robustez frente a ejemplos adversarios.

## Reproducción local

```bash
python3 -m venv venv
. venv/bin/activate
pip install tensorflow pillow numpy imageio
python3 solve.py
```

El script mantiene varias candidatas, muta una sola variable por iteración y ordena por confianza. La búsqueda es estocástica; conviene fijar una semilla para repetir resultados.

## Evidencia

- Predicción original y confianza.
- Cinco píxeles modificados y nueva etiqueta.
- Respuesta de la instancia, con la flag redactada.

## Lecciones aprendidas

- La precisión de un modelo no implica robustez.
- Restringir el número de píxeles no elimina el riesgo si se permite elegirlos.
- La búsqueda aleatoria guiada por confianza es suficiente para este modelo.

## Mitigaciones y detección

- Validar que la entrada sea similar a la original.
- Entrenar con ejemplos adversarios y limitar los cambios permitidos.
- No usar la predicción como única decisión de seguridad.
- Registrar entradas anómalas y confidencias inusuales.

## Referencias

- <https://www.hackthebox.com/challenges/267>
- <https://owasp.org/www-project-machine-learning-security-top-10/>
- <https://attack.mitre.org/techniques/T1548/>
