---
topic: Xamarin analysis
tags: [mobile, android, xamarin, dotnet, assembly, ilspy, dnspy]
---

# Xamarin analysis

**English** | [🇪🇸 Español](xamarin-analysis.md)

## Concept

Xamarin.Android apps package .NET assemblies inside the APK, often under `assemblies/` or compressed in `libmonodroid_bundle_app.so`. Logic can be opened with dnSpy, ILSpy or `ilspycmd` and often keeps useful class names and strings.

## When it applies

- An APK with `assemblies/` or `libmonodroid_bundle_app.so`.
- References to `Mono.Android`, `Xamarin.Forms` or `mscorlib`.
- Validation logic in C#.
- Obfuscation with cryptic names.

## Procedure

1. Unzip the APK and locate assemblies.
2. Extract or decompress the bundle if needed.
3. Open `Assembly-CSharp.dll` in dnSpy or ILSpy.
4. Search for validation methods and strings.
5. Recompile or patch the assembly if necessary.

```bash
unzip app.apk -d apk
find apk -iname '*.dll' -o -iname '*monodroid*'
ilspycmd apk/assemblies/Assembly-CSharp.dll > app.cs
grep -nE 'password|flag|secret|encrypt' app.cs | head
```

## Variants

- Assemblies inside `libmonodroid_bundle_app.so`.
- Obfuscation with ConfuserEx or Obfuscar.
- Logic in shared .NET MAUI libraries.
- IL patching and repackaging.

## Limitations

- The bundle may be compressed or encrypted.
- Obfuscation can hide names and flows.
- Recompiling may break the signature.
- Some logic may live in native code.

## Mitigation and detection

- Do not store secrets in assemblies.
- Validate on the server and sign the APK.
- Use obfuscation and integrity checks.
- Monitor modified versions and abnormal access.

## References

- <https://learn.microsoft.com/en-us/xamarin/android/>
- <https://github.com/icsharpcode/ILSpy>
- <https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/>
