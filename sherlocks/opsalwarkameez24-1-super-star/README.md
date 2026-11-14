---
sherlock: "OpSalwarKameez24-1: Super-Star"
category: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware-analysis, electron, app-asar, nodejs, websocket, shellcode]
---

# OpSalwarKameez24-1: Super-Star — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una campaña de phishing distribuye un cupón de descuento falso. El ejecutable es una aplicación Electron que muestra una interfaz de cupones. Se pide analizar el paquete y determinar qué hace en el sistema.

## Evidencias

- `Electron-Coupon.exe` y su instalador.
- `resources/app.asar`, `preload.js` y `script.jsc`.
- Captura de red del proceso.

```bash
file Electron-Coupon.exe
7z l Electron-Coupon.exe
```

## Investigación

### 1. Inventario y triaje

Se extrae el contenido del instalador y se localiza `app.asar`. `asar` empaqueta JavaScript y recursos; al extraerlo aparece `index.js`, `preload.js` y un módulo nativo.

```bash
npx asar extract app.asar app
ls -la app
```

### 2. Línea temporal

`index.js` crea una `BrowserWindow` con `nodeIntegration: true` y `contextIsolation: false`. La aplicación abre un WebSocket y captura las pulsaciones de los campos de entrada. El canal y el puerto aparecen en `preload.js`.

```bash
grep -RInE 'nodeIntegration|WebSocket|keydown|shellcode' app/
```

### 3. Artefacto clave

`script.jsc` contiene bytecode y una cadena base64. Un XOR con una clave corta produce shellcode; `strings` revela `VirtualAlloc`, `RtlMoveMemory` y `CreateThread`. El shellcode conecta a un C2 y ejecuta `cmd.exe`.

## Conclusiones

- La aplicación es un keylogger con ejecución de shellcode.
- `nodeIntegration` habilitado permite que el renderer acceda a Node.
- El C2 y el cupón falso son los IOC principales.
- El paquete Electron debe analizarse como malware, no como una app legítima.

## Lecciones

- `app.asar` no es cifrado: se extrae con `asar`.
- `nodeIntegration` convierte una web en código nativo.
- Un `.jsc` puede ocultar shellcode y APIs de Windows.
- La captura de red confirma el canal de exfiltración.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/luckystars0612/Sherlock-HTB/tree/main/SuperStar>
- <https://attack.mitre.org/techniques/T1056/001/>
