---
topic: Xamarin analysis
tags: [mobile, android, xamarin, dotnet, assembly, ilspy, dnspy]
---

# Xamarin analysis

[🌐 English](xamarin-analysis.en.md) | **Español**

## Concepto

Las apps Xamarin.Android empaquetan ensamblados .NET dentro del APK, a menudo en `assemblies/` o comprimidos en `libmonodroid_bundle_app.so`. La lógica se puede abrir con dnSpy, ILSpy o `ilspycmd` y suele conservar nombres de clases y cadenas útiles.

## Cuándo aplica

- APK con `assemblies/` o `libmonodroid_bundle_app.so`.
- Referencias a `Mono.Android`, `Xamarin.Forms` o `mscorlib`.
- Lógica de validación en C#.
- Ofuscación con nombres crípticos.

## Procedimiento

1. Descomprimir el APK y localizar ensamblados.
2. Extraer o descomprimir el bundle si es necesario.
3. Abrir `Assembly-CSharp.dll` en dnSpy o ILSpy.
4. Buscar métodos de validación y cadenas.
5. Recompilar o parchear el ensamblado si hace falta.

```bash
unzip app.apk -d apk
find apk -iname '*.dll' -o -iname '*monodroid*'
ilspycmd apk/assemblies/Assembly-CSharp.dll > app.cs
grep -nE 'password|flag|secret|encrypt' app.cs | head
```

## Variantes

- Ensamblados dentro de `libmonodroid_bundle_app.so`.
- Ofuscación con ConfuserEx u Obfuscar.
- Lógica en bibliotecas compartidas .NET MAUI.
- Parcheo de IL y reempaquetado.

## Limitaciones

- El bundle puede estar comprimido o cifrado.
- La ofuscación puede ocultar nombres y flujos.
- Recompilar puede romper la firma.
- Parte de la lógica puede estar en código nativo.

## Mitigación y detección

- No guardar secretos en ensamblados.
- Validar en servidor y firmar el APK.
- Usar ofuscación y comprobación de integridad.
- Monitorizar versiones modificadas y accesos anómalos.

## Referencias

- <https://learn.microsoft.com/en-us/xamarin/android/>
- <https://github.com/icsharpcode/ILSpy>
- <https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/>
