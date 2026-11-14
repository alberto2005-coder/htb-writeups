---
topic: SSH CA — firma de claves y suplantación
tags: [network, ssh, ca, certificates, privesc]
---

# SSH CA — firma de claves y suplantación

[🌐 English](ssh-certificate-authority.en.md) | **Español**

## Concepto

Un servidor SSH puede confiar en una CA mediante `TrustedUserCAKeys`. Quien obtenga la clave privada de la CA puede firmar una clave con cualquier principal, incluido root, y autenticarse sin conocer contraseñas.

## Cuándo aplica

- `/etc/ssh/sshd_config` con `TrustedUserCAKeys`.
- Claves `ca` y `ca.pub` accesibles por un usuario.
- Automatizaciones que firman claves con una CA compartida.

## Procedimiento

1. Buscar `TrustedUserCAKeys` y ficheros `ca`/`ca.pub`.
2. Comprobar si la clave privada de la CA es legible.
3. Firmar una clave pública con el principal de root.
4. Usar la clave firmada para iniciar sesión.
5. Validar el certificado con `ssh-keygen -L`.

## Comandos

```bash
ssh-keygen -t ed25519 -f user_key -N ''
ssh-keygen -s ca -I audit -n root -V +1d user_key.pub
ssh-keygen -L -f user_key-cert.pub
ssh -i user_key root@<HOST>
```

## Variantes

- Principal comodín o `*` en `AuthorizedPrincipalsFile`.
- Certificados de host para suplantar servidores.
- CA antigua sin revocación ni `Serial`.

## Limitaciones

- La clave privada de la CA debe ser accesible.
- `sshd` puede limitar principals con `Match`.
- Los certificados pueden estar revocados con KRL.

## Mitigación

- Proteger la clave de la CA y separarla del servidor.
- Limitar principals y usar `AuthorizedPrincipalsCommand`.
- Configurar revocación y caducidad corta.

## Detección

- Certificados firmados fuera del proceso de aprovisionamiento.
- Logins con `root` mediante certificado y `Serial` desconocido.

## Referencias

- <https://man.openbsd.org/sshd_config#TrustedUserCAKeys>
- <https://attack.mitre.org/techniques/T1550/>
