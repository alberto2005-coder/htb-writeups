---
machine: Blurry
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, clearml, pickle, pytorch, deserialization]
---

# Blurry — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

ClearML es vulnerable a deserialización de artefactos pickle (CVE-2024-24590) y entrega una shell. La escalada usa un evaluador PyTorch ejecutado como root: un `.pth` malicioso se ejecuta al importar el modelo y evade la detección de Fickling.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
curl -s http://blurry.htb/ | head
# Artefacto pickle malicioso subido a ClearML
python3 clearml_pickle.py --url http://blurry.htb:8080
# Evaluador PyTorch
sudo -l
find / -name "*.pth" 2>/dev/null
```

## Enumeración

- Panel ClearML con registro abierto y proyectos de ejemplo.
- Artefactos y modelos subidos por la aplicación.
- Un script de evaluación de modelos se ejecuta periódicamente como root.

## Acceso inicial

Se crea una tarea y se sube un artefacto pickle malicioso. Cuando ClearML lo recupera y deserializa, ejecuta el payload y devuelve una shell como el usuario de la aplicación.

## Escalada de privilegios

El evaluador carga modelos PyTorch con `torch.load`. Un archivo `.pth` con código en `runpy` se ejecuta durante la importación; la comprobación con Fickling no lo detecta y el proceso corre como root.

## Evidencia

- Artefacto pickle ejecutado por ClearML.
- Shell como el usuario del servicio.
- Modelo `.pth` cargado por el evaluador root.

## Lecciones aprendidas

- Pickle es código, no un formato de datos seguro.
- Las herramientas de detección tienen bypasses; la aislamiento importa más.
- Un evaluador de modelos root convierte un artefacto en ejecución privilegiada.

## Mitigación y detección

- No deserializar artefactos de usuarios no confiables.
- Ejecutar ClearML y los evaluadores sin privilegios, en contenedores efímeros.
- Firmar modelos y usar formatos seguros como Safetensors.

## Referencias

- [0xdf — Blurry](https://0xdf.gitlab.io/2024/10/12/htb-blurry.html)
- [NVD — CVE-2024-24590](https://nvd.nist.gov/vuln/detail/CVE-2024-24590)
- [Hack The Box — Blurry](https://app.hackthebox.com/machines/blurry)
