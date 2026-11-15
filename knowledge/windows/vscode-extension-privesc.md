---
topic: VS Code — extensiones maliciosas en trabajos de sincronización
tags: [windows, vscode, extension, sync, privesc]
---

# VS Code — extensiones maliciosas en trabajos de sincronización

[🌐 English](vscode-extension-privesc.en.md) | **Español**

## Concepto

VS Code instala extensiones desde un `.vsix` y ejecuta su código al activarse. Si un trabajo de sincronización lee paquetes de un share escribible, un atacante publica una extensión con el mismo identificador y consigue ejecución en el contexto del usuario que sincroniza, a menudo con más privilegios.

## Cuándo aplica

- Un share de extensiones o perfiles es escribible.
- Un proceso programa `code --install-extension` o sincroniza perfiles.
- La extensión se activa al abrir el editor o un workspace.

## Procedimiento

1. Localizar el share y el proceso de sincronización.
2. Crear una extensión con `package.json` y un `activate`.
3. Empaquetar el `.vsix` y colocarlo en el share.
4. Esperar la instalación y la ejecución del comando.

## Comandos

```bash
smbclient //<HOST>/<SHARE> -U <USER>%<PASS>
vsce package
smbclient //<HOST>/<SHARE> -U <USER>%<PASS> -c "put extension.vsix"
code --install-extension extension.vsix
# package.json
{"name":"ext","publisher":"x","version":"1.0.0","engines":{"vscode":"*"},"main":"./extension.js","activationEvents":["*"]}
```

## Variantes

- Reemplazar una extensión legítima por versión superior.
- Usar un perfil o workspace confiable ya suscrito.
- Aprovechar tareas de VS Code que ejecutan comandos al abrir.

## Limitaciones

- El share debe permitir escritura.
- La extensión debe ser compatible con la versión de VS Code.
- El usuario debe reiniciar o abrir el workspace.

## Mitigación

- Firmar y validar extensiones; usar un marketplace interno.
- Montar shares de sincronización como solo lectura.
- Revisar extensiones y permisos de workspace.

## Detección

- `.vsix` nuevos en shares de sincronización.
- Extensiones con `activationEvents: ["*"]`.
- Procesos hijos de VS Code ejecutando comandos.

## Referencias

- [VS Code — Extension manifest](https://code.visualstudio.com/api/references/extension-manifest)
- [0xdf — Checkpoint](https://0xdf.gitlab.io/2026/10/24/htb-checkpoint.html)
- [CWE-829 — Inclusion of Functionality from Untrusted Control Sphere](https://cwe.mitre.org/data/definitions/829.html)
