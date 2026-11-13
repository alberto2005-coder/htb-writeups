---
challenge: SeeTheSharpFlag
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, xamarin, dotnet, decompilation]
---

# SeeTheSharpFlag — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app uses Xamarin/.NET. .NET assemblies ship inside the APK and can be decompiled with ILSpy or dnSpy. The check and the flag appear in managed code.

## Prompt and surface

- Mobile, Easy, retired.
- An APK from a Xamarin app is provided.
- The screen asks for input and validates the result.

```bash
unzip -l app.apk | grep -Ei 'assemblies|dll|mono'
```

## Reconnaissance

- The APK contains `assemblies/` and Mono libraries.
- The `.dll` files are .NET assemblies, not native code.
- `file` on the assemblies confirms the PE/.NET format.

```bash
unzip -o app.apk -d apk
find apk -iname '*.dll' -o -iname '*.exe'
file apk/assemblies/*.dll
```

## Analysis

The main assembly is opened with ILSpy or `ilspycmd`. Validation classes, constants and comparison calls are located. The flag may be a constant or built from several strings.

```bash
ilspycmd apk/assemblies/SeeTheSharpFlag.dll > decompiled.cs
grep -nE 'flag|password|check|Equals|Compare' decompiled.cs | head -n 40
```

## Exploitation

1. Extract the assemblies from the APK.
2. Identify the method that decides success.
3. Read the constant or reproduce the transformation.
4. Enter the value in the app or calculate the flag.

Running the app or patching the APK is unnecessary when the logic is static.

## Evidence

- Assembly list.
- Snippet of the validation method.
- Calculated value and success screen, with the flag redacted.

## Lessons learned

- Xamarin compiles to IL, not Java bytecode.
- Assemblies inside the APK are fully trusted code to the analyst.
- .NET obfuscation is reversible with the right tools.

## Mitigations and detection

- Do not store secrets in client assemblies.
- Validate server-side and use attestation.
- Obfuscate with integrity checks.
- Detect rebuilt APKs and modified assemblies.

## References

- <https://www.hackthebox.com/challenges/SeeTheSharpFlag>
- <https://github.com/icsharpcode/ILSpy>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1552/>
