---
title: Inyección de contexto y autocompletado en modelos
tags: [ai, llm, prompt-injection, path-traversal, rce]
---

# Inyección de contexto y autocompletado en modelos

[🇬🇧 English](lm-context-injection.en.md) | **Español**

## 1. Cuándo mirar aquí

Una app carga documentos como «contexto» de un modelo y responde preguntas sobre ellos. Si el documento lo elige el usuario, el atacante decide qué lee el modelo. Si además hay una función de autocompletar código que se ejecuta, el fallo escala a RCE.

## 2. El patrón

```python
def get_repository(topic):
    for suffix in ["", ".md"]:
        path = f"{knowledge_path}/{topic}{suffix}"
        if os.path.exists(path):
            return read_file(path)
    return None
```

- `topic` se concatena sin normalizar: `../config.py` sale del directorio permitido.
- El contenido se guarda con `store_doc()` y el modelo lo usa para responder.
- Preguntando por una clave presente en el documento, el modelo la repite.

No hace falta «romper» el modelo: se le da contexto envenenado y se le pregunta.

## 3. De fuga a ejecución

Si existe un endpoint que completa código y lo ejecuta:

```python
completion = lm.code(params.code)
full_code = params.code + completion.strip()
return {"result": eval_code(full_code)}
```

Se escribe la llamada a medias y se deja que el modelo genere la línea que falta:

```python
import os
cmd = "id"
# run cmd with system
```

El modelo completa `os.system(cmd)`. La clave de API del endpoint suele estar en el mismo `config.py` que se filtró.

## 4. Variantes

- **Path traversal** en el nombre del documento, como arriba.
- **Documento envenenado**: un PDF o Markdown con instrucciones ocultas que el modelo obedece al resumirlo.
- **RAG sin aislamiento**: el índice mezcla documentos de distintos usuarios y el modelo filtra datos de otro.
- **Salida ejecutada**: `eval`, `exec`, `subprocess` o `child_process` sobre texto generado.

## 5. Mitigación

- `os.path.realpath` y comprobar que el resultado empieza por el directorio permitido; rechazar `..` y rutas absolutas.
- Lista blanca de documentos por usuario y por sesión; no un directorio global.
- Secretos fuera del árbol servido y rotación tras una fuga.
- No ejecutar nunca código generado por un modelo; si se ofrece autocompletado, que sea texto y sin `eval`.
- Tratar la salida del modelo como entrada no confiable (OWASP LLM05).

## 6. Detección

- Peticiones con `..`, `/` o `%2e%2e` en campos que nombran documentos.
- Llamadas al endpoint de autocompletar con fragmentos incompletos y seguido de procesos `python3`/`sh`.
- Volumen anómalo de preguntas sobre «configuración», «claves» o «contraseñas» en el chat.

## 7. Errores típicos

- **Confiar en `os.path.exists`**: acepta `..`; no valida nada.
- **Cifrar la clave y dejarla en el mismo fichero**: el traversal la entrega igual.
- **Probar solo prompts «maliciosos»**: el fallo está en el contexto, no en la frase.

MITRE ATLAS: AML.T0051 (LLM prompt injection). Referencias: OWASP Top 10 for LLM (LLM01, LLM05), CWE-22 y la documentación de `languagemodels`.
