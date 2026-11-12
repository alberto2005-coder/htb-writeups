---
topic: JuicyPotato
tags: [windows, privilege-escalation, seimpersonate, juicy-potato, com]
---

# JuicyPotato

[🇬🇧 English](juicy-potato.en.md) | **Español**

## Concepto

JuicyPotato abusa de `SeImpersonatePrivilege` o `SeAssignPrimaryTokenPrivilege` para ejecutar un proceso como SYSTEM. Coacciona a un servidor COM para autenticarse contra un RPC local controlado y roba el token resultante.

## Cuándo aplica

- Cuenta con `SeImpersonatePrivilege` (IIS, MSSQL, servicios).
- Windows anterior a las mitigaciones de 2019 o sin parche.
- Hay un CLSID COM válido para la versión/arquitectura.

## Requisitos

1. `whoami /priv` con el privilegio habilitado.
2. Binario JuicyPotato y payload.
3. CLSID compatible (según SO).
4. Puerto libre para el listener local.

## Procedimiento

```powershell
whoami /priv
JuicyPotato.exe -l 1337 -p cmd.exe -a "/c whoami > C:\\temp\\out.txt" -t * -c {<CLSID>}
```

`-l` es el puerto local, `-p` el programa, `-a` los argumentos, `-t *` prueba ambos tipos de token y `-c` el CLSID. Si funciona, el proceso se ejecuta como SYSTEM.

Para una reverse shell:

```powershell
JuicyPotato.exe -l 1337 -p powershell.exe -a "-e <base64>" -t * -c {<CLSID>}
```

## Variantes

- **RoguePotato**: para versiones donde JuicyPotato falla.
- **PrintSpoofer**: abusa de named pipes de spooler.
- **SweetPotato**: combina varios vectores.
- **GodPotato**: soporta más versiones de Windows.

## Limitaciones

- Microsoft corrigió el vector en Windows 10 1809+/Server 2019 con cambios COM.
- El CLSID debe existir y ser adecuado.
- EDR puede bloquear la coacción o el token.
- Requiere un privilegio que no siempre está presente.

## Mitigación

- Eliminar `SeImpersonatePrivilege` de cuentas de servicio cuando sea posible.
- Aplicar parches y mitigaciones COM.
- Ejecutar servicios con cuentas de bajo privilegio.
- Bloquear binarios no firmados y monitorizar tokens.

## Detección

- Procesos que crean servidores RPC locales inusuales.
- `SeImpersonatePrivilege` en cuentas web.
- Creación de procesos SYSTEM desde servicios.
- Binarios Potato/PrintSpoofer en disco.

MITRE ATT&CK: T1134 (Access Token Manipulation), T1068 (Exploitation for Privilege Escalation).

## Referencias

- <https://github.com/ohpe/juicy-potato>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/>
- <https://attack.mitre.org/techniques/T1134/>
