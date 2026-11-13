---
challenge: Don't Overreact
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, react-native, javascript, hardcoded-secret]
---

# Don't Overreact — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app está construida con React Native. La lógica y los secretos viajan en `index.android.bundle`, un JavaScript empaquetado pero no cifrado. Al desempaquetarlo y embellecerlo se recupera la validación y la flag.

## Enunciado y superficie

- Mobile, Easy, retirado.
- Se entrega un APK.
- La app muestra una pantalla que pide una entrada y valida el resultado.

```bash
unzip -l app.apk | head -n 30
```

## Reconocimiento

- El APK contiene `assets/index.android.bundle`, típico de React Native.
- El bundle es JavaScript minificado; no está compilado a bytecode Android.
- `strings` ya revela rutas y posibles cadenas de validación.

```bash
unzip -p app.apk assets/index.android.bundle > index.android.bundle
file index.android.bundle
npx js-beautify index.android.bundle > bundle.pretty.js
```

## Análisis

Se busca la lógica de comparación y las cadenas que participan en ella. En React Native es habitual encontrar la validación, la clave y el mensaje de éxito en el mismo módulo.

```bash
grep -nE 'flag|secret|check|validate|atob|decrypt' bundle.pretty.js | head -n 40
```

Si el valor está codificado, se reproduce la función de decodificación en Node en lugar de ejecutar la app.

```bash
node -e "console.log(Buffer.from('<BASE64>','base64').toString())"
```

## Explotación

1. Extraer el bundle del APK.
2. Embellecerlo y localizar la función que decide el éxito.
3. Identificar la entrada esperada o la transformación inversa.
4. Introducirla en la app o calcular la flag directamente.

No se necesita parchear el APK ni modificar la firma.

## Evidencia

- Ruta del bundle y tamaño.
- Fragmento de la función de validación.
- Entrada calculada y pantalla de éxito, con la flag redactada.

## Lecciones aprendidas

- React Native no oculta la lógica: solo la empaqueta.
- La minificación no es ofuscación fuerte.
- Los secretos en el cliente son públicos por definición.

## Mitigaciones y detección

- No incluir claves ni validaciones definitivas en el bundle.
- Validar en el servidor y usar atestación de app.
- Ofuscar y dividir el código como defensa en profundidad.
- Detectar bundles modificados y firmas no esperadas.

## Referencias

- <https://www.hackthebox.com/challenges/Don%27t%20Overreact>
- <https://reactnative.dev/docs/performance>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1552/>
