---
topic: Cracking de Passpie con PGP
tags: [crypto, passpie, pgp, john, credentials]
---

# Cracking de Passpie con PGP

[🌐 English](passpie-pgp-cracking.en.md) | **Español**

## Concepto

Passpie cifra las contraseñas con una clave PGP protegida por una passphrase. Si el directorio `.passpie` es accesible, la clave se extrae y se crackea offline; después la herramienta descifra las entradas.

## Cuándo aplica

- Directorio `~/.passpie` legible por el usuario comprometido.
- Clave PGP con passphrase débil.
- Contraseñas de root o de servicio almacenadas en Passpie.

## Procedimiento

1. Localizar `.passpie` y la clave privada.
2. Extraer el hash con `gpg2john`.
3. Crackear con John o Hashcat.
4. Usar `passpie copy` para recuperar la credencial.

```bash
ls -la ~/.passpie
gpg2john ~/.passpie/.keys > passpie.hash
john --wordlist=/usr/share/wordlists/rockyou.txt passpie.hash
passpie copy --to stdout
# Otra entrada:
passpie copy <SERVICE> --to stdout
```

## Variantes

- Clave PGP sin passphrase.
- Backup de `.passpie` en un share o un ZIP.
- Passphrase reutilizada de otro servicio.
- Entradas exportadas a texto plano.

## Limitaciones

- La clave debe estar disponible y no protegida por hardware.
- Una passphrase fuerte hace inviable el cracking.
- La versión de Passpie puede cambiar el formato.

## Mitigación y detección

- Proteger `.passpie` con permisos estrictos y una passphrase fuerte.
- Usar una clave hardware o un gestor con cifrado por entrada.
- Rotar las credenciales almacenadas tras una intrusión.

## Referencias

- <https://github.com/marcwebbie/passpie>
- <https://github.com/openwall/john/blob/bleeding-jumbo/doc/README.gpg>
- <https://gnupg.org/documentation/>
