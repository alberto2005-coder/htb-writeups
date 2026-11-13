---
topic: Adversarial examples
tags: [ai, machine-learning, evasion, robustness, image-classification]
---

# Adversarial examples

[🇬🇧 English](adversarial-examples.en.md) | **Español**

## Concepto

Un ejemplo adversario es una entrada modificada de forma deliberada para que un modelo de machine learning produzca una predicción incorrecta. La perturbación puede ser invisible o estar limitada a unos pocos píxeles, pero explota la frontera de decisión aprendida por el modelo.

No es un fallo de memoria ni una inyección: es una falta de robustez frente a entradas fuera de la distribución de entrenamiento.

## Cuándo aplica

- Clasificadores de imágenes, texto o audio expuestos a usuarios.
- Sistemas que aceptan archivos o parámetros controlados por el atacante.
- Modelos usados como control de acceso, moderación o detección.
- Retos donde se permite modificar un número limitado de valores.

## Requisitos y condiciones

- Acceso al modelo o a una API que devuelva etiqueta y confianza.
- Capacidad de modificar la entrada dentro de un presupuesto.
- Conocimiento de las clases y del formato de entrada.
- En muchos casos, el modelo es conocido (*white-box*); en otros basta la salida (*black-box*).

## Procedimiento

1. Reproducir la predicción original y medir la confianza.
2. Definir una función objetivo: maximizar la confianza de una clase incorrecta.
3. Generar perturbaciones aleatorias dentro del presupuesto permitido.
4. Conservar las mejores candidatas y mutar una variable cada vez.
5. Validar localmente antes de enviar a la API.
6. Comprobar que la etiqueta cambió y que la entrada sigue siendo válida.

```python
pred, conf = model.predict_one(image)
score = max(conf[0][target_classes])
```

Para ataques white-box se pueden usar gradientes (FGSM, PGD). Para black-box, búsqueda aleatoria, optimización evolutiva o *transfer attack* desde un modelo sustituto.

## Variantes

- **FGSM:** una perturbación en la dirección del gradiente.
- **PGD:** iteraciones de FGSM con proyección al presupuesto.
- **Patch adversarial:** modifica una región concreta de la imagen.
- **Data poisoning:** altera el entrenamiento, no solo la inferencia.
- **Prompt injection:** equivalente en modelos de lenguaje, con instrucciones en la entrada.

## Limitaciones

- La perturbación puede no transferirse entre modelos.
- El presupuesto de cambios suele estar limitado por la aplicación.
- La confianza no siempre refleja robustez.
- Un ejemplo válido para una versión puede fallar tras reentrenar.

## Mitigación

- Entrenar con ejemplos adversarios.
- Validar similitud con la entrada original.
- Limitar el número y la magnitud de los cambios permitidos.
- Usar ensembles y detección de anomalías.
- No basar una decisión de seguridad únicamente en la predicción.

## Detección

- Registrar entradas con confianza anómala o cambios mínimos.
- Comparar la entrada con la original y con la distribución esperada.
- Alertar sobre patrones de prueba repetidos desde una misma cuenta.
- Monitorizar consultas que maximizan clases concretas.

## Referencias

- <https://owasp.org/www-project-machine-learning-security-top-10/>
- <https://arxiv.org/abs/1412.6572>
- <https://attack.mitre.org/techniques/T1548/>
