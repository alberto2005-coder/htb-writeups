---
sherlock: Dream Job-2
category: Threat Intelligence
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, lazarus, dratzarus, torisma, malware]
---

# Dream Job-2 — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Continuación de Dream Job-1. Se pide analizar el malware y las herramientas propias que Lazarus usó en la campaña, relacionarlas con MITRE ATT&CK y extraer indicadores reutilizables.

## Evidencias

- ZIP anidado con una muestra y una nota de seguridad.
- El segundo ZIP requiere otra contraseña indicada en la nota.
- No se ejecuta la muestra: solo análisis estático y de inteligencia.

```bash
7z l DreamJob2.zip
sha256sum *
strings -a sample | head
```

## Investigación

### 1. Inventario y triaje

Se identifican los archivos internos, se calculan hashes y se separa la muestra de la documentación. La nota advierte que el contenido es malware: se trabaja en una VM aislada.

### 2. Herramientas y familia

```text
DRATzarus: RAT asociado a Lazarus
Torisma: loader/backdoor con packing lz4 y cifrado VEST-32
```

Se contrastan nombres, cadenas y funciones con la documentación de MITRE y con informes públicos. Se anota qué características son observables en la muestra y cuáles provienen de la literatura.

### 3. Artefacto clave

La nota y el nombre del malware permiten navegar por ATT&CK. Se buscan técnicas de ejecución, persistencia, cifrado y C2, y se descartan las que no estén respaldadas por la evidencia.

## Conclusiones

- La campaña usa malware propio además de herramientas públicas.
- DRATzarus y Torisma aportan acceso remoto y evasión.
- Los IOC deben correlacionarse con la infraestructura de Dream Job-1.
- El impacto sigue siendo espionaje dirigido.

## Lecciones

- El análisis estático evita ejecutar muestras peligrosas.
- La inteligencia de malware se valida con varias fuentes.
- Nombrar una familia no sustituye la evidencia de sus capacidades.

## Referencias

- <https://www.hackthebox.com/sherlocks/Dream%20Job-2>
- <https://attack.mitre.org/campaigns/C0022/>
- <https://attack.mitre.org/groups/G0032/>
