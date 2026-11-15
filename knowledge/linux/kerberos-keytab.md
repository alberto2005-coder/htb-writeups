---
topic: Kerberos — keytabs y autenticación SSH
tags: [linux, kerberos, keytab, ssh, privesc]
---

# Kerberos — keytabs y autenticación SSH

[🌐 English](kerberos-keytab.en.md) | **Español**

## Concepto

Un keytab contiene claves de una entidad Kerberos y permite obtener tickets sin contraseña. Si se encuentra en un backup o en un directorio accesible, se puede usar con `kinit -kt` para autenticarse como ese usuario. SSH con GSSAPI acepta el ticket y otorga acceso sin conocer la contraseña.

## Cuándo aplica

- Hay un archivo `.keytab` accesible o en un backup.
- SSH tiene `GSSAPIAuthentication yes`.
- El servicio Kerberos es alcanzable.

## Procedimiento

1. Localizar y copiar el keytab.
2. Listar sus entradas con `klist -kt`.
3. Obtener un ticket con `kinit -kt`.
4. Conectarse por SSH con `-K` y el usuario correspondiente.

## Comandos

```bash
find / -name "*.keytab" 2>/dev/null
klist -kt <FILE>.keytab
kinit -kt <FILE>.keytab <USER>
klist
ssh -K <USER>@<HOST>
```

## Variantes

- Usar el keytab de una cuenta de servicio para Kerberoasting.
- Extraer hashes con `keytabextract`.
- Combinar con `impacket` para obtener un TGT.

## Limitaciones

- El keytab debe pertenecer a una cuenta válida.
- El reloj debe estar sincronizado.
- SSH debe permitir GSSAPI y el usuario debe existir.

## Mitigación

- Proteger keytabs y rotar claves periódicamente.
- Restringir SSH GSSAPI a cuentas necesarias.
- No incluir keytabs en backups accesibles.

## Detección

- Lectura de keytabs fuera de servicios.
- Tickets Kerberos emitidos para cuentas de servicio.
- Conexiones SSH con GSSAPI desde hosts no habituales.

## Referencias

- [MIT Kerberos — keytab](https://web.mit.edu/kerberos/krb5-latest/doc/basic/keytab_def.html)
- [0xdf — Tentacle](https://0xdf.gitlab.io/2021/06/19/htb-tentacle.html)
- [CWE-522 — Insufficiently Protected Credentials](https://cwe.mitre.org/data/definitions/522.html)
