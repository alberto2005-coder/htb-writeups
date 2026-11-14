---
topic: ThemeBleed CVE-2023-38146
tags: [windows, themebleed, cve-2023-38146, msstyles, dll]
---

# ThemeBleed CVE-2023-38146

[🌐 English](themebleed.en.md) | **Español**

## Concepto

ThemeBleed es una vulnerabilidad del cargador de temas de Windows 11. Un archivo `.msstyles` manipulado hace que el sistema resuelva una ruta UNC y cargue una DLL controlada por el atacante al previsualizar el tema.

## Cuándo aplica

- Windows 11 sin el parche de septiembre de 2023.
- El usuario abre o previsualiza un archivo `.theme`/`.msstyles`.
- El atacante puede alojar una DLL en un recurso UNC accesible.

## Procedimiento

1. Crear un tema con un `.msstyles` que apunte a un recurso UNC.
2. Alojar una DLL que se ejecute al cargarse.
3. Entregar el tema y esperar la previsualización.
4. Confirmar la ejecución en el contexto del usuario.

```powershell
# Construir el .msstyles y la DLL, alojar en \<HOST>\share
# Abrir el .theme en el objetivo
```

## Variantes

- DLL con reverse shell o loader.
- Ruta UNC con credenciales para capturar NetNTLM.
- Cadena con un fallo de elevación posterior.

## Limitaciones

- El objetivo debe previsualizar el tema.
- La ruta UNC debe ser accesible.
- El parche de Windows bloquea la carga.

## Mitigación

- Actualizar Windows.
- Bloquear temas no confiables y UNC saliente.
- Deshabilitar la previsualización automática.

## Detección

- Creación de `.msstyles`/`.theme` en descargas.
- Conexiones SMB salientes a hosts no habituales.
- Carga de DLL desde rutas de red por `explorer.exe`.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2023-38146>
- <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-38146>
- <https://attack.mitre.org/techniques/T1222/>
