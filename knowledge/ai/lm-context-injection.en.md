---
title: Context injection and autocompletion in language models
tags: [ai, llm, prompt-injection, path-traversal, rce]
---

# Context injection and autocompletion in language models

**English** | [🇪🇸 Español](lm-context-injection.md)

## 1. When to look here

An app loads documents as a model's "context" and answers questions about them. If the user picks the document, the attacker decides what the model reads. If there is also a code-autocompletion feature that executes its output, the flaw escalates to RCE.

## 2. The pattern

```python
def get_repository(topic):
    for suffix in ["", ".md"]:
        path = f"{knowledge_path}/{topic}{suffix}"
        if os.path.exists(path):
            return read_file(path)
    return None
```

- `topic` is concatenated without normalising: `../config.py` escapes the allowed directory.
- The content is stored with `store_doc()` and used by the model to answer.
- Ask for a key present in the document and the model repeats it.

No need to "break" the model: give it poisoned context and ask.

## 3. From leak to execution

If an endpoint completes code and runs it:

```python
completion = lm.code(params.code)
full_code = params.code + completion.strip()
return {"result": eval_code(full_code)}
```

Write the call halfway and let the model generate the missing line:

```python
import os
cmd = "id"
# run cmd with system
```

The model completes `os.system(cmd)`. The endpoint's API key usually lives in the same `config.py` that was leaked.

## 4. Variants

- **Path traversal** in the document name, as above.
- **Poisoned document**: a PDF or Markdown with hidden instructions the model obeys when summarising.
- **RAG without isolation**: the index mixes documents from different users and the model leaks another's data.
- **Executed output**: `eval`, `exec`, `subprocess` or `child_process` on generated text.

## 5. Mitigation

- `os.path.realpath` plus a prefix check against the allowed directory; reject `..` and absolute paths.
- Per-user, per-session document allowlists; not one global directory.
- Keep secrets outside the served tree and rotate after a leak.
- Never execute model-generated code; if autocompletion is offered, keep it text-only with no `eval`.
- Treat model output as untrusted input (OWASP LLM05).

## 6. Detection

- Requests with `..`, `/` or `%2e%2e` in document-name fields.
- Calls to the completion endpoint with partial snippets followed by `python3`/`sh` processes.
- Anomalous volume of questions about "config", "keys" or "passwords" in chat.

## 7. Typical errors

- **Trusting `os.path.exists`**: it accepts `..`; it validates nothing.
- **Encrypting the key but leaving it in the same file**: traversal hands it over anyway.
- **Only trying "malicious" prompts**: the flaw is in the context, not the sentence.

MITRE ATLAS: AML.T0051 (LLM prompt injection). References: OWASP Top 10 for LLM (LLM01, LLM05), CWE-22 and the `languagemodels` documentation.
