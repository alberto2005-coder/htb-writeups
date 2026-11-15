---
topic: RCE en aplicaciones Electron
tags: [linux, electron, asar, ipc, prototype-pollution, rce]
---

# RCE en aplicaciones Electron

[🌐 English](electron-ipc-rce.en.md) | **Español**

## Concepto

Una aplicación Electron incluye el código del cliente en `app.asar`. Si el renderer puede invocar handlers IPC peligrosos o contaminar prototypes, una entrada controlada por el usuario puede ejecutar comandos en el proceso principal.

## Cuándo aplica

- Aplicaciones Electron que descargan o procesan contenido externo.
- `contextIsolation` deshabilitado o `nodeIntegration` activo.
- Handlers IPC que pasan datos a `exec`, `spawn` o `shell.openExternal`.

## Procedimiento

1. Extraer `app.asar` y revisar `main.js`, `preload.js` y handlers IPC.
2. Identificar el canal expuesto y el formato de datos.
3. Probar un payload de contaminación de prototipos o un comando.
4. Confirmar la ejecución en el proceso principal.

```bash
npx asar extract app.asar app
rg -n 'ipcMain|contextBridge|exec|spawn|openExternal' app
# Enviar el payload al canal IPC descubierto
curl -s -X POST http://<HOST>:3000/api/run -H 'Content-Type: application/json' \
  -d '{"__proto__":{"shell":true},"cmd":"id"}'
```

## Variantes

- `shell.openExternal` con una URL `file://` o un esquema peligroso.
- Prototype pollution en opciones de `child_process`.
- LFI en el cargador de recursos.
- Actualizador sin firma que descarga un paquete malicioso.

## Limitaciones

- El canal IPC debe estar expuesto al contenido controlable.
- `contextIsolation` y sandbox pueden bloquear el ataque.
- La versión de Electron debe permitir el gadget.

## Mitigación y detección

- Actualizar Electron y habilitar `contextIsolation`/sandbox.
- Validar y allowlist de canales IPC y URLs externas.
- Congelar prototipos y no pasar datos del renderer a `exec`.

## Referencias

- <https://www.electronjs.org/docs/latest/tutorial/security>
- <https://github.com/electron/asar>
- <https://owasp.org/www-community/vulnerabilities/Prototype_Pollution>
