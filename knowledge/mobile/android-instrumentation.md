---
topic: Android instrumentation
tags: [mobile, android, frida, smali, root-detection, ssl-hook, instrumentation]
---

# Android instrumentation

[🌐 English](android-instrumentation.en.md) | **Español**

## Concepto

La instrumentación dinámica permite modificar una app en ejecución sin recompilarla. Frida hookea métodos Java y funciones nativas; el parcheo smali cambia el bytecode antes de reconstruir el APK. Es la vía habitual para saltar root detection, validaciones y pinning.

## Cuándo aplica

- App con root detection o comprobaciones de integridad.
- Validación de contraseña en cliente.
- Pinning Java o nativo.
- Necesidad de observar argumentos y valores de retorno.

## Procedimiento

1. Descompilar con `apktool` y localizar la comprobación.
2. Elegir parcheo smali o hook dinámico.
3. Ejecutar `frida-server` con permisos de root.
4. Hookear el método o la función nativa.
5. Verificar que el flujo cambia y que la app sigue estable.

```bash
apktool d app.apk -o app
grep -RInE 'isRooted|su|frida|if-eqz|if-ne' app/smali | head
frida -U -f <PACKAGE> -l hook.js --no-pause
```

```javascript
Java.perform(function () {
  var Root = Java.use('com.scottyab.rootbeer.RootBeer');
  Root.isRooted.implementation = function () { return false; };
});
```

## Variantes

- Parcheo smali con `if-eqz`/`if-ne` y recompilación.
- Hook de `SSL_CTX_set_cert_verify_callback`.
- Bypass de `RootBeer`, `SafetyNet` o comprobaciones propias.
- Uso de `objection` para tareas comunes.

## Limitaciones

- Algunas apps detectan Frida o el entorno modificado.
- El pinning nativo requiere localizar la función correcta.
- Recompilar invalida la firma original.
- Los emuladores antiguos simplifican o cambian el comportamiento.

## Mitigación y detección

- Combinar root detection con atestación de integridad.
- Ofuscar comprobaciones y dispersarlas.
- Verificar firma, APK y bibliotecas nativas.
- Detectar Frida, hooks y proxies en telemetría.

## Referencias

- <https://frida.re/docs/android/>
- <https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/>
- <https://github.com/sensepost/objection>
