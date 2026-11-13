---
sherlock: ReliableThreat
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, vscode-extension, supply-chain, windows, powershell, persistence]
---

# ReliableThreat — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una extensión de Visual Studio Code aparentemente legítima empieza a ejecutar comandos tras una actualización. Se pide reconstruir la cadena de infección, los archivos implicados y las acciones del atacante.

## Evidencias

- Directorio de extensiones de VS Code y su historial de instalación.
- Scripts de PowerShell y archivos de configuración de la extensión.
- Logs de proceso, red y persistencia de Windows.
- Eventos de ejecución y artefactos del perfil del usuario.

```bash
sha256sum <EXTENSION>.vsix
7z l <EXTENSION>.vsix
```

## Investigación

### 1. Inventario y triaje

Se localiza la extensión instalada y se compara su contenido con la versión pública. Los archivos `package.json`, `extension.js` y los scripts auxiliares son el punto de partida.

```bash
Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Directory
Get-Content "$env:USERPROFILE\.vscode\extensions\<EXT>\package.json"
```

### 2. Línea temporal

- Instalación o actualización de la extensión.
- Primera ejecución del proceso hijo.
- Descarga de un segundo stage.
- Creación de persistencia y conexiones salientes.

Se cruzan los eventos de PowerShell con los procesos iniciados por `Code.exe`.

### 3. Artefacto clave

El script de activación de la extensión contiene la lógica que descarga y ejecuta el payload. La ofuscación se revierte y se identifican la URL, el comando y la ruta de persistencia.

```powershell
Get-Content <EXT>\extension.js | Select-String -Pattern 'http|powershell|cmd|Run'
```

## Conclusiones

- La extensión legítima fue modificada o suplantada.
- El primer stage ejecutó PowerShell desde el proceso del editor.
- El segundo stage estableció persistencia y C2.
- IOCs: hash, URL, ruta y nombre del proceso, redactados.

## Lecciones

- Las extensiones del editor son código con privilegios del usuario.
- Una actualización puede introducir un cambio malicioso sin cambiar el nombre.
- La cadena se entiende mejor cruzando procesos, red y persistencia.

## Referencias

- <https://www.hackthebox.com/sherlocks/ReliableThreat>
- <https://code.visualstudio.com/docs/editor/extension-marketplace>
- <https://attack.mitre.org/techniques/T1195/001/>
